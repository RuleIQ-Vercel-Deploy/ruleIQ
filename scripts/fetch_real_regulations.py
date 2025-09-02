"""
from __future__ import annotations

Fetch real regulation data from official APIs and update Neo4j with actual requirements and penalties.
This replaces our guessed/generated data with real compliance requirements.
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
sys.path.append(str(Path(__file__).parent.parent))
from services.api.regulation_api_client import RegulationAPIClient
from neo4j import AsyncGraphDatabase
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegulationDataFetcher:
    """Fetches real regulation data and updates Neo4j."""

    def __init__(self):
        self.neo4j_uri = 'bolt://localhost:7688'
        self.neo4j_user = 'neo4j'
        self.neo4j_password = 'ruleiq123'
        self.driver = AsyncGraphDatabase.driver(self.neo4j_uri, auth=(self.
            neo4j_user, self.neo4j_password))

    async def close(self) ->None:
        """Close connections."""
        await self.driver.close()

    async def get_uk_legislation_urls(self) ->List[Dict[str, str]]:
        """Get all UK legislation URLs from manifests."""
        urls = []
        manifest_dir = Path('data/manifests')
        for manifest_file in manifest_dir.glob('*.json'):
            with open(manifest_file, 'r') as f:
                data = json.load(f)
                if 'items' in data:
                    for item in data['items']:
                        if 'url' in item and item['url']:
                            url = item['url']
                            if 'legislation.gov.uk' in url:
                                urls.append({'id': item['id'], 'url': url,
                                    'title': item.get('title', 'Unknown'),
                                    'manifest': manifest_file.name})
        logger.info('Found %s UK legislation URLs' % len(urls))
        return urls

    async def fetch_and_update_regulation(self, reg_info: Dict[str, str],
        client: RegulationAPIClient) ->Dict[str, Any]:
        """Fetch regulation data and update Neo4j."""
        logger.info('Processing %s: %s' % (reg_info['id'], reg_info['url']))
        result = await client.fetch_uk_legislation(reg_info['url'])
        if not result['success']:
            logger.error('Failed to fetch %s: %s' % (reg_info['id'], result
                .get('error')))
            return {'id': reg_info['id'], 'success': False, 'error': result
                .get('error')}
        async with self.driver.session() as session:
            await session.run(
                """
                MATCH (r:Regulation {id: $id})
                SET r.has_real_data = true,
                    r.real_requirements_count = $req_count,
                    r.real_penalties_count = $penalty_count,
                    r.real_controls = $controls,
                    r.data_fetched_at = $fetched_at,
                    r.real_title = $title,
                    r.real_description = $description
                RETURN r.id
            """
                , id=reg_info['id'], req_count=len(result['requirements']),
                penalty_count=len(result['penalties']), controls=result[
                'controls'], fetched_at=result['fetched_at'], title=result[
                'metadata']['title'], description=result['metadata'][
                'description'])
            for req in result['requirements'][:10]:
                await session.run(
                    """
                    MATCH (r:Regulation {id: $reg_id})
                    MERGE (req:RealRequirement {
                        text: $text,
                        regulation_id: $reg_id,
                    })
                    MERGE (r)-[:HAS_REAL_REQUIREMENT]->(req)
                    SET req.type = $type,
                        req.keywords = $keywords,
                        req.provision_id = $provision_id
                """
                    , reg_id=reg_info['id'], text=req['text'][:500], type=
                    req['type'], keywords=req.get('keywords', []),
                    provision_id=req.get('id', ''))
            for penalty in result['penalties'][:5]:
                penalty_text = json.dumps(penalty)
                await session.run(
                    """
                    MATCH (r:Regulation {id: $reg_id})
                    MERGE (p:RealPenalty {
                        description: $description,
                        regulation_id: $reg_id,
                    })
                    MERGE (r)-[:HAS_REAL_PENALTY]->(p)
                    SET p.type = $type,
                        p.amount = $amount
                """
                    , reg_id=reg_info['id'], description=penalty_text[:500],
                    type=penalty['type'], amount=penalty.get('amount',
                    'Not specified'))
            if result.get('enforcement'):
                await session.run(
                    """
                    MATCH (r:Regulation {id: $id})
                    SET r.enforcement_authorities = $authorities,
                        r.enforcement_powers = $powers
                """
                    , id=reg_info['id'], authorities=result['enforcement'].
                    get('authority', []), powers=result['enforcement'].get(
                    'powers', [])[:3])
        logger.info('✅ Updated %s with %s requirements, %s penalties' % (
            reg_info['id'], len(result['requirements']), len(result[
            'penalties'])))
        return {'id': reg_info['id'], 'success': True, 'requirements': len(
            result['requirements']), 'penalties': len(result['penalties']),
            'controls': len(result['controls'])}

    async def process_all_regulations(self, batch_size: int=5, resume_from:
        int=0) ->Optional[Any]:
        """Process all UK legislation URLs with checkpoint support."""
        urls = await self.get_uk_legislation_urls()
        if not urls:
            logger.warning('No UK legislation URLs found')
            return
        checkpoint_file = Path('data/regulation_fetch_checkpoint.json')
        if checkpoint_file.exists() and resume_from == 0:
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                resume_from = checkpoint.get('last_batch_index', 0)
                logger.info('Resuming from batch %s' % (resume_from //
                    batch_size + 1))
        results = []
        async with RegulationAPIClient() as client:
            for i in range(resume_from, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                logger.info('\nProcessing batch %s/%s' % (i // batch_size +
                    1, (len(urls) - 1) // batch_size + 1))
                tasks = [self.fetch_and_update_regulation(reg, client) for
                    reg in batch]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                with open(checkpoint_file, 'w') as f:
                    json.dump({'last_batch_index': i + batch_size,
                        'total_processed': i + len(batch), 'total_urls':
                        len(urls)}, f)
                if i + batch_size < len(urls):
                    await asyncio.sleep(2)
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        report = {'timestamp': datetime.now().isoformat(),
            'total_processed': len(results), 'successful': successful,
            'failed': failed, 'results': results}
        with open('data/real_regulation_fetch_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        logger.info('\n%s' % ('=' * 60))
        logger.info('Fetching complete: %s/%s successful' % (successful,
            len(results)))
        logger.info('Report saved to data/real_regulation_fetch_report.json')
        return report


async def main() ->None:
    """Main execution."""
    fetcher = RegulationDataFetcher()
    try:
        logger.info('Starting real regulation data fetch...')
        logger.info(
            'This will replace generated data with actual legal requirements')
        report = await fetcher.process_all_regulations(batch_size=3)
        if report:
            logger.info(
                '\n✅ Successfully fetched real data for %s regulations' %
                report['successful'])
            logger.info(
                'The ruleIQ platform now has REAL compliance requirements!')
    except Exception as e:
        logger.error('Error: %s' % e)
        import traceback
        traceback.print_exc()
    finally:
        await fetcher.close()


if __name__ == '__main__':
    asyncio.run(main())
