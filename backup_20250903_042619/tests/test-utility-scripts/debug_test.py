import logging
logger = logging.getLogger(__name__)
import asyncio
import statistics
import time
from unittest.mock import Mock
from sqlalchemy.ext.asyncio import AsyncSession
from services.ai.assistant import ComplianceAssistant


async def test_model_selection():
    """Debug the model selection test."""
    mock_db = Mock(spec=AsyncSession)
    compliance_assistant = ComplianceAssistant(mock_db)
    performance_config = {'max_response_time': 3.0, 'min_throughput': 10,
        'max_memory_mb': 500, 'target_success_rate': 0.95,
        'concurrent_users': [1, 5, 10, 20], 'test_duration': 30}
    selection_times = []
    try:
        for i in range(5):
            logger.info('Iteration %s' % (i + 1))
            start_time = time.time()
            model = compliance_assistant._get_task_appropriate_model('analysis'
                , {'framework': 'gdpr', 'prompt_length': 1000})
            selection_time = time.time() - start_time
            selection_times.append(selection_time)
            logger.info('Model: %s, Selection time: %ss' % (type(model),
                selection_time))
            assert model is not None, f'Model is None at iteration {i + 1}'
        avg_time = statistics.mean(selection_times)
        max_time = max(selection_times)
        logger.info('Average time: %ss' % avg_time)
        logger.info('Max time: %ss' % max_time)
        assert avg_time < 0.01, f'Average selection time {avg_time:.3f}s too slow'
        assert max_time < 0.05, f'Max selection time {max_time:.3f}s too slow'
        logger.info('All assertions passed!')
    except Exception as e:
        logger.info('Error occurred: %s' % e)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(test_model_selection())
