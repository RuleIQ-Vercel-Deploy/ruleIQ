import { withRequestLogging } from '../../lib/logging/utils';

import type { NextApiRequest, NextApiResponse } from 'next';

type HealthStatus = {
  status: 'ok';
  version: string;
  timestamp: string;
};

function handler(_req: NextApiRequest, res: NextApiResponse<HealthStatus>) {
  res.status(200).json({
    status: 'ok',
    version: process.env['APP_VERSION'] || '1.0.0',
    timestamp: new Date().toISOString(),
  });
}

export default withRequestLogging(handler);
