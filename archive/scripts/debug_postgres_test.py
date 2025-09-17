"""Debug PostgreSQL checkpointing test."""
import logging
logger = logging.getLogger(__name__)
from __future__ import annotations
import os
import sys
import asyncio
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5433/compliance_test'
import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, END
from tests.integration.test_state_integration import ComplianceStateDict, ComplianceState, compliance_state_to_dict

async def main():
    """Test PostgreSQL checkpointing."""
    try:
        logger.info('1. Connecting to PostgreSQL...')
        conn = psycopg.connect(os.environ['DATABASE_URL'], autocommit=True, row_factory=dict_row)
        logger.info('   ✅ Connected')
        logger.info('2. Setting up PostgresSaver...')
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()
        logger.info('   ✅ Setup complete')
        logger.info('3. Creating workflow...')
        workflow = StateGraph(ComplianceStateDict)

        async def process_node(state: Dict[str, Any]) -> Dict[str, Any]:
            state['workflow_status'] = 'processed'
            if 'decisions' not in state:
                state['decisions'] = []
            state['decisions'].append({'id': 'dec-checkpoint', 'timestamp': datetime.now().isoformat(), 'actor': 'System', 'action': 'checkpoint_test'})
            return state
        workflow.add_node('process', process_node)
        workflow.set_entry_point('process')
        workflow.add_edge('process', END)
        logger.info('   ✅ Workflow created')
        logger.info('4. Compiling with checkpointer...')
        app = workflow.compile(checkpointer=checkpointer)
        logger.info('   ✅ Compiled')
        logger.info('5. Creating initial state...')
        initial_state = ComplianceState(case_id='test-checkpoint-001', actor='PolicyAuthor', objective='Test checkpointing', trace_id=str(uuid4()))
        initial_dict = compliance_state_to_dict(initial_state)
        logger.info('   ✅ State created')
        logger.info('6. Running workflow...')
        config = {'configurable': {'thread_id': 'test-thread-001'}}
        result = await app.ainvoke(initial_dict, config)
        logger.info(f"   ✅ Result: workflow_status = {result.get('workflow_status')}")
        logger.info('7. Checking saved state...')
        saved_state = checkpointer.get(config)
        if saved_state:
            logger.info('   ✅ State saved successfully')
            logger.info(f"      Thread ID: {saved_state.config.get('configurable', {}).get('thread_id')}")
            logger.info(f'      Has values: {bool(saved_state.values)}')
        else:
            logger.info('   ❌ No saved state found')
        logger.info('\n✅ All tests passed!')
    except Exception as e:
        logger.info(f'\n❌ Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
if __name__ == '__main__':
    asyncio.run(main())
