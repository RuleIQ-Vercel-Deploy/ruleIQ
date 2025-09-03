"""Fix function signature mismatches (S930 violations)."""
import logging
logger = logging.getLogger(__name__)
import os
import re

def fix_notification_signatures() -> None:
    """Fix the notification function signature mismatches."""
    filepath = 'langgraph_agent/nodes/notification_nodes.py'
    if not os.path.exists(filepath):
        logger.info(f'File {filepath} not found')
        return
    with open(filepath, 'r') as f:
        content = f.read()
    content = re.sub('await self\\._send_email_notification\\(\\s*recipient=', 'await self._send_email_notification(\n                recipient_email=', content)
    content = re.sub('await self\\._send_sms_notification\\(\\s*recipient=([^,]+),\\s*message=', 'await self._send_sms_notification(\\n                phone_number=\\1,\\n                message=', content)
    content = re.sub('await self\\._send_slack_notification\\(\\s*channel_id=([^,]+),\\s*message=([^)]+)\\)', 'await self._send_slack_notification(\\n                channel=\\1,\\n                message=\\2)', content)
    with open(filepath, 'w') as f:
        f.write(content)
    logger.info(f'✓ Fixed function signatures in {filepath}')

def check_sms_signature() -> None:
    """Check and fix SMS notification signature."""
    filepath = 'langgraph_agent/nodes/notification_nodes.py'
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'def _send_sms_notification' in line:
            logger.info(f'Found SMS notification definition at line {i + 1}')
            for j in range(i, min(i + 5, len(lines))):
                logger.info(f'  Line {j + 1}: {lines[j].rstrip()}')

def check_slack_signature() -> None:
    """Check and fix Slack notification signature."""
    filepath = 'langgraph_agent/nodes/notification_nodes.py'
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'def _send_slack_notification' in line:
            logger.info(f'Found Slack notification definition at line {i + 1}')
            for j in range(i, min(i + 5, len(lines))):
                logger.info(f'  Line {j + 1}: {lines[j].rstrip()}')
if __name__ == '__main__':
    logger.info('Checking function signatures...')
    check_sms_signature()
    logger.info()
    check_slack_signature()
    logger.info()
    logger.info('Fixing function signature mismatches...')
    fix_notification_signatures()
    logger.info('\n✅ Function signature fixes complete!')