import React, { useState, useEffect, useRef } from 'react';
import { ChevronsUpDown, Search, Bell, Menu, X, ChevronDown, ChevronRight, PlusCircle, Filter, Upload, MoreHorizontal, ArrowRight, Bot, Send, User, Shield, Settings, BarChart, HardDrive, GitBranch, Briefcase, FileText, CheckCircle, Clock, AlertTriangle, GanttChartSquare, ClipboardCheck, History, LogOut, LifeBuoy } from 'lucide-react';
import { Recharts, ResponsiveContainer, BarChart as RechartsBarChart, Bar, XAxis, YAxis, Tooltip, Legend, LineChart, Line, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

// Mock Data
const MOCK_FRAMEWORKS = [
  { id: 'soc2', name: 'SOC 2' },
  { id: 'iso27001', name: 'ISO 27001' },
  { id: 'hipaa', name: 'HIPAA' },
  { id: 'pci-dss', name: 'PCI DSS' },
];

const MOCK_POLICIES = [
    { id: 'pol-001', name: 'Information Security Policy', status: 'Approved', version: 3, lastUpdated: '2025-05-15' },
    { id: 'pol-002', name: 'Acceptable Use Policy', status: 'Approved', version: 2, lastUpdated: '2025-05-10' },
    { id: 'pol-003', name: 'Data Classification Policy', status: 'Draft', version: 1, lastUpdated: '2025-06-10' },
    { id: 'pol-004', name: 'Incident Response Plan', status: 'In Review', version: 1, lastUpdated: '2025-06-18' },
    { id: 'pol-005', name: 'Disaster Recovery Plan', status: 'Archived', version: 4, lastUpdated: '2024-12-20' },
];

const MOCK_TASKS = {
    'To Do': [
        { id: 'task-1', content: 'Define data encryption standards', owner: 'Alex Green', control: 'C-05', dueDate: '2025-07-15' },
        { id: 'task-2', content: 'Configure firewall rules', owner: 'Sam Rivera', control: 'C-12', dueDate: '2025-07-20' },
    ],
    'In Progress': [
        { id: 'task-3', content: 'Conduct employee security training', owner: 'Casey Jordan', control: 'A-02', dueDate: '2025-06-30', progress: 50 },
    ],
    'Done': [
        { id: 'task-4', content: 'Implement MFA for all critical systems', owner: 'Alex Green', control: 'A-01', dueDate: '2025-06-01', progress: 100 },
    ]
};

const MOCK_EVIDENCE = [
    { id: 'ev-001', name: 'Q2 Vulnerability Scan Report', control: 'V-03', source: 'AWS Security Hub', quality: 'Good', expiry: '2025-08-01', type: 'Automated', preview: 'PDF' },
    { id: 'ev-002', name: 'Employee Training Records', control: 'A-02', source: 'Manual Upload', quality: 'Fair', expiry: '2026-01-10', type: 'Manual', preview: 'CSV' },
    { id: 'ev-003', name: 'Firewall Configuration Screenshot', control: 'C-12', source: 'Manual Upload', quality: 'Excellent', expiry: 'N/A', type: 'Manual', preview: 'PNG' },
];

const MOCK_GAPS = [
    { id: 'gap-01', control: 'BCP-04', description: 'Business continuity plan has not been tested in the last 12 months.', recommendation: 'Schedule and conduct a full business continuity drill. Document outcomes and any issues found.' },
    { id: 'gap-02', control: 'HR-02', description: 'Background checks are not consistently performed for new hires with access to sensitive data.', recommendation: 'Update HR policy to mandate background checks for all relevant roles and verify compliance for recent hires.' },
];

const MOCK_NOTIFICATIONS = [
    { id: 'n-1', type: 'Alert', message: 'Evidence "Q1 Pen Test Report" expires in 7 days.', time: '1h ago', read: false },
    { id: 'n-2', type: 'Update', message: 'Integration with Google Workspace failed to sync.', time: '3h ago', read: false },
    { id: 'n-3', type: 'Info', message: 'Policy "Data Classification Policy" was approved by Jane Doe.', time: '1d ago', read: true },
];

const MOCK_TEAM = [
    { id: 'u-1', name: 'Admin User', email: 'admin@example.com', role: 'Owner', lastLogin: '2025-06-18T16:00:00Z', mfa: true },
    { id: 'u-2', name: 'Jane Doe', email: 'jane.doe@example.com', role: 'Editor', lastLogin: '2025-06-18T14:30:00Z', mfa: true },
    { id: 'u-3', name: 'John Auditor', email: 'john.auditor@external.com', role: 'Auditor', lastLogin: '2025-06-17T10:00:00Z', mfa: false },
];

const MOCK_AUDIT_LOGS = [
    { id: 'log-1', user: 'Admin User', action: 'Updated user role', target: 'Jane Doe to Editor', timestamp: '2025-06-18T14:05:12Z' },
    { id: 'log-2', user: 'System', action: 'Integration sync failed', target: 'Google Workspace', timestamp: '2025-06-18T13:00:45Z' },
    { id: 'log-3', user: 'Jane Doe', action: 'Approved policy', target: 'Information Security Policy', timestamp: '2025-06-18T11:55:01Z' },
];


// UI Components (shadcn/ui style)

const Card = ({ children, className = '' }) => <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm p-6 ${className}`}>{children}</div>;
const Button = ({ children, variant = 'default', className = '', ...props }) => {
    const variants = {
        default: 'bg-blue-600 text-white hover:bg-blue-700',
        destructive: 'bg-red-600 text-white hover:bg-red-700',
        outline: 'bg-transparent border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700',
        secondary: 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600',
        ghost: 'hover:bg-gray-100 dark:hover:bg-gray-700',
        link: 'text-blue-600 hover:underline',
    };
    return <button className={`px-4 py-2 rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${variants[variant]} ${className}`} {...props}>{children}</button>
};
const Input = ({ className = '', ...props }) => <input className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-transparent focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${className}`} {...props} />;
const Progress = ({ value, className = '' }) => <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 ${className}`}><div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${value}%` }}></div></div>;
const Badge = ({ children, variant = 'default', className = '' }) => {
    const variants = {
        default: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        destructive: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    };
    return <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>{children}</span>
};
const DropdownMenu = ({ trigger, children }) => {
    const [isOpen, setIsOpen] = useState(false);
    const ref = useRef(null);
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (ref.current && !ref.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [ref]);
    return (
        <div className="relative inline-block text-left" ref={ref}>
            <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>
            {isOpen && (
                <div className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 z-10">
                    <div className="py-1" role="menu" aria-orientation="vertical">
                        {children}
                    </div>
                </div>
            )}
        </div>
    );
};
const DropdownMenuItem = ({ children, onClick }) => <a href="#" className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700" role="menuitem" onClick={onClick}>{children}</a>;
const Dialog = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-lg mx-4">
                <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                    <h3 className="text-lg font-semibold">{title}</h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
                </div>
                <div className="p-6">{children}</div>
            </div>
        </div>
    );
};
const Sheet = ({ isOpen, onClose, children, side='right' }) => {
  const sideClasses = {
    right: 'inset-y-0 right-0',
    left: 'inset-y-0 left-0',
  }
  return (
    <div className={`fixed inset-0 z-40 ${isOpen ? '' : 'pointer-events-none'}`}>
      {/* Overlay */}
      <div className={`absolute inset-0 bg-black bg-opacity-50 transition-opacity ${isOpen ? 'opacity-100' : 'opacity-0'}`} onClick={onClose}></div>
      {/* Content */}
      <div className={`fixed ${sideClasses[side]} flex flex-col w-full max-w-md bg-white dark:bg-gray-800 shadow-xl transition-transform transform ${isOpen ? 'translate-x-0' : (side === 'right' ? 'translate-x-full' : '-translate-x-full')}`}>
          {children}
      </div>
    </div>
  )
}

// Sub-Components
const OnboardingWizard = () => {
    const [step, setStep] = useState(1);
    const [profile, setProfile] = useState({ businessName: '', industry: '', headcount: '' });
    const [frameworks, setFrameworks] = useState([]);
    const totalSteps = 3;

    const handleProfileChange = (e) => {
        const { name, value } = e.target;
        setProfile(prev => ({ ...prev, [name]: value }));
    };

    const toggleFramework = (id) => {
        setFrameworks(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]);
    };

    const estimatedControls = frameworks.length * 15 + (parseInt(profile.headcount) || 0) / 10;

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-8">
            <h1 className="text-3xl font-bold mb-2">Welcome! Let's get you set up.</h1>
            <p className="text-gray-500 mb-8">This will only take a couple of minutes.</p>
            <Progress value={(step / totalSteps) * 100} className="mb-8" />
            <Card>
                {step === 1 && (
                    <div>
                        <h2 className="text-xl font-semibold mb-4">1. Business Profile</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Business Name</label>
                                <Input name="businessName" value={profile.businessName} onChange={handleProfileChange} placeholder="e.g. Innovate Inc." />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Industry</label>
                                <Input name="industry" value={profile.industry} onChange={handleProfileChange} placeholder="e.g. SaaS" />
                            </div>
                             <div>
                                <label className="block text-sm font-medium mb-1">Headcount</label>
                                <Input type="number" name="headcount" value={profile.headcount} onChange={handleProfileChange} placeholder="e.g. 50" />
                            </div>
                        </div>
                    </div>
                )}
                {step === 2 && (
                    <div>
                        <h2 className="text-xl font-semibold mb-4">2. Select Frameworks</h2>
                        <p className="text-gray-500 mb-4">Choose the compliance frameworks you want to work with.</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {MOCK_FRAMEWORKS.map(fw => (
                                <div key={fw.id} onClick={() => toggleFramework(fw.id)} className={`p-4 border rounded-lg cursor-pointer ${frameworks.includes(fw.id) ? 'bg-blue-50 border-blue-500 ring-2 ring-blue-500' : 'bg-transparent border-gray-300 dark:border-gray-600'}`}>
                                    <h3 className="font-semibold">{fw.name}</h3>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                {step === 3 && (
                    <div>
                        <h2 className="text-xl font-semibold mb-4">3. Review & Confirm</h2>
                        <p className="mb-4">Here's a summary of your setup. You can always change this later.</p>
                        <div className="space-y-2 mb-6">
                            <p><strong>Business Name:</strong> {profile.businessName}</p>
                            <p><strong>Industry:</strong> {profile.industry}</p>
                            <p><strong>Headcount:</strong> {profile.headcount}</p>
                            <p><strong>Frameworks:</strong> {frameworks.map(f => MOCK_FRAMEWORKS.find(mf => mf.id === f).name).join(', ')}</p>
                        </div>
                        <div className="bg-blue-50 dark:bg-blue-900/50 p-4 rounded-lg">
                            <h3 className="font-semibold text-blue-800 dark:text-blue-200">Real-time Estimate</h3>
                            <p className="text-blue-700 dark:text-blue-300">You're looking at approximately <strong>{Math.round(estimatedControls)}</strong> controls to implement.</p>
                        </div>
                    </div>
                )}
                <div className="flex justify-between mt-8">
                    <Button variant="outline" onClick={() => setStep(s => Math.max(1, s - 1))} disabled={step === 1}>Back</Button>
                    {step < totalSteps && <Button onClick={() => setStep(s => Math.min(totalSteps, s + 1))}>Next</Button>}
                    {step === totalSteps && <Button>Finish Setup</Button>}
                </div>
            </Card>
        </div>
    );
};

const ComplianceDashboard = () => {
    const readinessScore = 68;
    const dashboardData = {
        gaps: 12,
        expiring: 3,
        highRisk: 5,
    };
    const activity = [
        { user: 'Alex G.', action: 'uploaded evidence for C-05', time: '2h ago' },
        { user: 'System', action: 'synced 52 assets from AWS', time: '5h ago' },
        { user: 'Casey J.', action: 'approved "Access Control Policy"', time: '1d ago' },
    ];
    const chartData = [
        { name: 'Jan', Implemented: 30, Pending: 20 },
        { name: 'Feb', Implemented: 45, Pending: 15 },
        { name: 'Mar', Implemented: 60, Pending: 12 },
        { name: 'Apr', Implemented: 70, Pending: 10 },
        { name: 'May', Implemented: 85, Pending: 8 },
        { name: 'Jun', Implemented: readinessScore, Pending: 100 - readinessScore },
    ];

    return (
        <div className="p-4 md:p-8 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Dashboard</h1>
                 <div className="flex items-center gap-2">
                    <Input type="date" className="w-auto" defaultValue="2025-06-01"/>
                    <span className="text-gray-500">to</span>
                    <Input type="date" className="w-auto" defaultValue="2025-06-30"/>
                    <DropdownMenu trigger={<Button variant="outline">Export <ChevronDown size={16} className="ml-2 inline"/></Button>}>
                        <DropdownMenuItem>Export as CSV</DropdownMenuItem>
                        <DropdownMenuItem>Export as PDF</DropdownMenuItem>
                    </DropdownMenu>
                </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="flex flex-col justify-center items-center text-center">
                    <h3 className="text-lg font-semibold text-gray-500 mb-2">Readiness Score</h3>
                    <div className="relative">
                        <svg className="w-32 h-32" viewBox="0 0 36 36">
                          <path className="text-gray-200 dark:text-gray-700" strokeWidth="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                          <path className="text-blue-600" strokeWidth="3" strokeDasharray={`${readinessScore}, 100`} fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        </svg>
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-3xl font-bold">{readinessScore}%</div>
                    </div>
                </Card>
                <Card className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer">
                    <h3 className="font-semibold text-gray-500">Open Gaps</h3>
                    <p className="text-4xl font-bold text-yellow-500">{dashboardData.gaps}</p>
                    <p className="text-sm text-gray-400 mt-2">Remediation required</p>
                </Card>
                <Card className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer">
                    <h3 className="font-semibold text-gray-500">Expiring Evidence</h3>
                    <p className="text-4xl font-bold text-red-500">{dashboardData.expiring}</p>
                    <p className="text-sm text-gray-400 mt-2">Within 30 days</p>
                </Card>
                <Card className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer">
                    <h3 className="font-semibold text-gray-500">High-Risk Controls</h3>
                    <p className="text-4xl font-bold">{dashboardData.highRisk}</p>
                    <p className="text-sm text-gray-400 mt-2">Unimplemented</p>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2">
                    <h3 className="font-semibold mb-4">Control Implementation Progress</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="Implemented" stroke="#3b82f6" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </Card>
                <Card>
                    <h3 className="font-semibold mb-4">Latest Activity</h3>
                    <ul className="space-y-4">
                        {activity.map((item, index) => (
                            <li key={index} className="flex items-start">
                                <User className="w-5 h-5 mr-3 mt-1 text-gray-400" />
                                <div>
                                    <p>{item.user} <span className="text-gray-500">{item.action}</span></p>
                                    <p className="text-sm text-gray-400">{item.time}</p>
                                </div>
                            </li>
                        ))}
                    </ul>
                </Card>
            </div>
        </div>
    );
};

const PolicyWorkspace = () => {
    const [isDiffVisible, setDiffVisible] = useState(false);
    const [isRegenPanelOpen, setRegenPanelOpen] = useState(false);

    const getStatusBadge = (status) => {
        switch (status) {
            case 'Approved': return <Badge variant="success">Approved</Badge>;
            case 'Draft': return <Badge>Draft</Badge>;
            case 'In Review': return <Badge variant="warning">In Review</Badge>;
            case 'Archived': return <Badge variant="secondary">Archived</Badge>;
            default: return <Badge>{status}</Badge>;
        }
    };

    return (
        <div className="p-4 md:p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Policy Workspace</h1>
                <Button><PlusCircle size={16} className="mr-2"/> Create Policy</Button>
            </div>
            
            <div className="flex">
                <div className="flex-grow">
                    <Card>
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b dark:border-gray-700">
                                    <th className="p-4">Policy Name</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4">Version</th>
                                    <th className="p-4">Last Updated</th>
                                    <th className="p-4">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {MOCK_POLICIES.map(policy => (
                                    <tr key={policy.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                        <td className="p-4 font-medium">{policy.name}</td>
                                        <td className="p-4">{getStatusBadge(policy.status)}</td>
                                        <td className="p-4 text-gray-500">{`v${policy.version}.0`}</td>
                                        <td className="p-4 text-gray-500">{policy.lastUpdated}</td>
                                        <td className="p-4">
                                            <DropdownMenu trigger={<Button variant="ghost" size="sm"><MoreHorizontal size={16}/></Button>}>
                                                <DropdownMenuItem>Edit</DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => setDiffVisible(true)}>View History</DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => setRegenPanelOpen(true)}>AI Regenerate</DropdownMenuItem>
                                                <DropdownMenuItem>Download DOCX</DropdownMenuItem>
                                                <DropdownMenuItem>Download PDF</DropdownMenuItem>
                                            </DropdownMenu>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>
                </div>
                {isRegenPanelOpen && (
                    <div className="w-80 ml-6 flex-shrink-0">
                       <Card>
                           <div className="flex justify-between items-center mb-4">
                                <h3 className="font-semibold">AI Regenerate</h3>
                               <button onClick={() => setRegenPanelOpen(false)}><X size={18}/></button>
                           </div>
                           <p className="text-sm text-gray-500 mb-4">Regenerate sections of the 'Data Classification Policy'.</p>
                           <label className="block text-sm font-medium mb-1">Tone</label>
                           <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-transparent mb-4">
                               <option>Formal</option>
                               <option>Simple</option>
                           </select>
                           <label className="block text-sm font-medium mb-1">Prompt</label>
                           <textarea className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-transparent h-32 mb-4" placeholder="e.g., Add a section about handling PII data according to GDPR."></textarea>
                           <Button className="w-full">Regenerate</Button>
                       </Card>
                    </div>
                )}
            </div>
            
            <Dialog isOpen={isDiffVisible} onClose={() => setDiffVisible(false)} title="Version History: Information Security Policy">
                <p>Showing differences between <strong>v2.0</strong> and <strong>v3.0</strong>.</p>
                <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-md font-mono text-sm">
                    <p className="text-red-500">- 2.1 All employees must use company-approved devices.</p>
                    <p className="text-green-500">+ 2.1 All employees and contractors must use company-managed or approved devices.</p>
                    <p className="text-gray-500">... rest of diff ...</p>
                </div>
                <div className="mt-6 flex justify-end gap-2">
                    <Button variant="outline" onClick={() => alert('Approval workflow started.')}>Request Approval</Button>
                    <Button onClick={() => setDiffVisible(false)}>Close</Button>
                </div>
            </Dialog>
        </div>
    );
};

const ImplementationPlanner = () => {
    const [tasks, setTasks] = useState(MOCK_TASKS);
    
    const burndownData = [
      { day: 1, remaining: 40 }, { day: 2, remaining: 38 },
      { day: 3, remaining: 35 }, { day: 4, remaining: 32 },
      { day: 5, remaining: 32 }, { day: 6, remaining: 28 },
      { day: 7, remaining: 25 },
    ];

    return (
        <div className="p-4 md:p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Implementation Planner</h1>
                <div className="flex gap-2">
                    <Button variant="outline">Bulk Edit</Button>
                    <Button><PlusCircle size={16} className="mr-2"/> Create Task</Button>
                </div>
            </div>

            <Card className="mb-6">
                <h3 className="font-semibold mb-2">Progress Burndown Chart</h3>
                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={burndownData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                        <YAxis label={{ value: 'Tasks Remaining', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Line type="monotone" dataKey="remaining" stroke="#ef4444" strokeWidth={2} name="Remaining Tasks" />
                    </LineChart>
                </ResponsiveContainer>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Object.entries(tasks).map(([columnId, column]) => (
                    <div key={columnId}>
                        <h2 className="text-lg font-semibold mb-4 px-1">{columnId} ({column.length})</h2>
                        <div className="space-y-4 bg-gray-100 dark:bg-gray-900 p-4 rounded-lg min-h-[300px]">
                            {column.map(task => (
                                <Card key={task.id} className="cursor-grab">
                                    <p className="font-semibold mb-2">{task.content}</p>
                                    <div className="flex justify-between items-center text-sm text-gray-500">
                                        <Badge>{task.control}</Badge>
                                        <span>{task.owner}</span>
                                    </div>
                                    <p className="text-sm text-red-500 mt-2">Due: {task.dueDate}</p>
                                    {task.progress && <Progress value={task.progress} className="mt-3"/>}
                                </Card>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

const EvidenceRepository = () => {
    const [isUploadSidebarOpen, setUploadSidebarOpen] = useState(false);

    const getQualityBadge = (quality) => {
        switch (quality) {
            case 'Excellent': return <Badge variant="success">{quality}</Badge>;
            case 'Good': return <Badge variant="default">{quality}</Badge>;
            case 'Fair': return <Badge variant="warning">{quality}</Badge>;
            case 'Poor': return <Badge variant="destructive">{quality}</Badge>;
            default: return <Badge>{quality}</Badge>;
        }
    };
    
    return (
        <div className="p-4 md:p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Evidence Repository</h1>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setUploadSidebarOpen(true)}><Upload size={16} className="mr-2"/> Mass Upload</Button>
                    <div className="flex items-center gap-2">
                        <span className="text-sm">Automated</span>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" value="" className="sr-only peer" />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                        </label>
                        <span className="text-sm">Manual</span>
                    </div>
                </div>
            </div>

            <div className="flex gap-6">
                <div className="flex-grow">
                    <Card>
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b dark:border-gray-700">
                                    <th className="p-4">Evidence Name</th>
                                    <th className="p-4">Control</th>
                                    <th className="p-4">Source</th>
                                    <th className="p-4">Quality Score</th>
                                    <th className="p-4">Expiry</th>
                                    <th className="p-4">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {MOCK_EVIDENCE.map(item => (
                                    <tr key={item.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                        <td className="p-4 font-medium flex items-center">
                                            {item.type === 'Automated' ? <CheckCircle size={16} className="text-green-500 mr-2"/> : <User size={16} className="text-gray-400 mr-2"/>}
                                            {item.name}
                                        </td>
                                        <td className="p-4"><Badge>{item.control}</Badge></td>
                                        <td className="p-4">{item.source}</td>
                                        <td className="p-4">{getQualityBadge(item.quality)}</td>
                                        <td className="p-4 text-red-500">{item.expiry}</td>
                                        <td className="p-4">
                                            <DropdownMenu trigger={<Button variant="ghost" size="sm"><MoreHorizontal size={16}/></Button>}>
                                                <DropdownMenuItem>Preview {item.preview}</DropdownMenuItem>
                                                <DropdownMenuItem>Download</DropdownMenuItem>
                                                <DropdownMenuItem>Configure Reminders</DropdownMenuItem>
                                            </DropdownMenu>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>
                </div>
                {isUploadSidebarOpen && (
                    <div className="w-80 flex-shrink-0">
                       <Card>
                           <div className="flex justify-between items-center mb-4">
                               <h3 className="font-semibold">Mass Upload</h3>
                               <button onClick={() => setUploadSidebarOpen(false)}><X size={18}/></button>
                           </div>
                           <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500">
                               <Upload size={32} className="mx-auto text-gray-400 mb-2"/>
                               <p className="text-sm">Drag & drop files here or click to browse</p>
                           </div>
                           <h4 className="font-semibold mt-6 mb-2">Duplicate Check</h4>
                           <div className="p-3 bg-yellow-50 dark:bg-yellow-900/50 rounded-md">
                               <p className="text-sm text-yellow-800 dark:text-yellow-200"><AlertTriangle size={16} className="inline mr-1"/> "Q2_scan.pdf" looks similar to "Q2 Vulnerability Scan Report".</p>
                           </div>
                       </Card>
                    </div>
                )}
            </div>
        </div>
    );
};

const IntegrationsHub = () => (
    <div className="p-4 md:p-8">
        <h1 className="text-3xl font-bold mb-6">Integrations Hub</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
                <div className="flex items-center mb-4">
                    <img src="https://placehold.co/40x40/E8F0FE/3367D6?text=G" alt="Google Workspace Logo" className="rounded-md mr-4" />
                    <div>
                        <h3 className="text-lg font-semibold">Google Workspace</h3>
                        <Badge variant="success">Live</Badge>
                    </div>
                </div>
                <p className="text-sm text-gray-500 mb-4">Sync users, groups, and logs from your Google Workspace.</p>
                <div className="flex justify-between">
                    <Button variant="outline">Test Connection</Button>
                    <Button>Manage</Button>
                </div>
            </Card>
            <Card>
                <div className="flex items-center mb-4">
                     <img src="https://placehold.co/40x40/E6F2FC/0078D4?text=M" alt="Microsoft 365 Logo" className="rounded-md mr-4" />
                    <div>
                        <h3 className="text-lg font-semibold">Microsoft 365</h3>
                        <Badge>Coming Soon</Badge>
                    </div>
                </div>
                <p className="text-sm text-gray-500 mb-4">Connect to Azure AD, Intune, and other Microsoft services.</p>
                <Button disabled>Connect</Button>
            </Card>
            <Card>
                <div className="flex items-center mb-4">
                     <img src="https://placehold.co/40x40/FFF8E1/FF9900?text=A" alt="AWS Logo" className="rounded-md mr-4" />
                    <div>
                        <h3 className="text-lg font-semibold">AWS</h3>
                        <Badge variant="success">Live</Badge>
                    </div>
                </div>
                <p className="text-sm text-gray-500 mb-4">Monitor security posture with AWS Security Hub and Config.</p>
                 <div className="flex justify-between">
                    <Button variant="outline">Test Connection</Button>
                    <Button>Manage</Button>
                </div>
            </Card>
            {/* Add more integration cards */}
        </div>
    </div>
);

const ReadinessGapAnalysis = () => (
    <div className="p-4 md:p-8">
        <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Readiness / Gap Analysis</h1>
            <div className="flex gap-2">
                <Button variant="outline">Simulate Scope Change</Button>
                <Button variant="outline">Export Gap List</Button>
            </div>
        </div>
        <Card>
            <table className="w-full text-left">
                <thead>
                    <tr className="border-b dark:border-gray-700">
                        <th className="p-4">Control ID</th>
                        <th className="p-4 w-1/2">Description of Gap</th>
                        <th className="p-4 w-1/2">AI-Generated Advice</th>
                        <th className="p-4">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {MOCK_GAPS.map(gap => (
                        <tr key={gap.id} className="border-b dark:border-gray-700">
                            <td className="p-4 font-mono"><Badge>{gap.control}</Badge></td>
                            <td className="p-4">{gap.description}</td>
                            <td className="p-4 text-sm text-gray-500">{gap.recommendation}</td>
                            <td className="p-4"><Button>Create Task</Button></td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </Card>
    </div>
);

const ReportCenter = () => (
    <div className="p-4 md:p-8">
        <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Report Center</h1>
            <Button><PlusCircle size={16} className="mr-2"/> Generate Report</Button>
        </div>
        <Card>
            <h2 className="text-xl font-semibold mb-4">Download History</h2>
            <table className="w-full text-left">
                <thead>
                    <tr className="border-b dark:border-gray-700">
                        <th className="p-4">Report Name</th>
                        <th className="p-4">Frameworks</th>
                        <th className="p-4">Generated By</th>
                        <th className="p-4">Date</th>
                        <th className="p-4">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr className="border-b dark:border-gray-700">
                        <td className="p-4 font-medium">Q2 SOC 2 Audit Pack</td>
                        <td className="p-4">SOC 2</td>
                        <td className="p-4">Admin User</td>
                        <td className="p-4">2025-06-15</td>
                        <td className="p-4"><Button variant="link">Download PDF</Button></td>
                    </tr>
                    {/* More history items */}
                </tbody>
            </table>
        </Card>
    </div>
);

const TeamManagement = () => (
    <div className="p-4 md:p-8">
        <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Team & RBAC Management</h1>
            <Button><PlusCircle size={16} className="mr-2"/> Invite User</Button>
        </div>
        <Card>
            <table className="w-full text-left">
                <thead>
                    <tr className="border-b dark:border-gray-700">
                        <th className="p-4">User</th>
                        <th className="p-4">Role</th>
                        <th className="p-4">Last Login</th>
                        <th className="p-4">MFA</th>
                        <th className="p-4">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {MOCK_TEAM.map(user => (
                        <tr key={user.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                            <td className="p-4">
                                <p className="font-semibold">{user.name}</p>
                                <p className="text-sm text-gray-500">{user.email}</p>
                            </td>
                            <td className="p-4">{user.role}</td>
                            <td className="p-4">{new Date(user.lastLogin).toLocaleString()}</td>
                            <td className="p-4">
                                {user.mfa ? <Badge variant="success">Enabled</Badge> : <Badge variant="destructive">Disabled</Badge>}
                            </td>
                            <td className="p-4">
                                <Button variant="ghost">Edit</Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </Card>
    </div>
);


const SettingsPage = () => (
    <div className="p-4 md:p-8">
        <h1 className="text-3xl font-bold mb-6">Settings & Secrets</h1>
        <Card>
            <h2 className="text-xl font-semibold mb-4">API Keys</h2>
            <div className="space-y-4">
                <div className="flex justify-between items-center p-4 border rounded-lg">
                    <div>
                        <p className="font-semibold">Platform API Key</p>
                        <p className="font-mono text-sm text-gray-500">plat_sk_••••••••••••1234</p>
                    </div>
                    <Button variant="outline">Regenerate</Button>
                </div>
                {/* More keys */}
            </div>
            <h2 className="text-xl font-semibold mt-8 mb-4">AI Configuration</h2>
            <div className="space-y-4">
                 <div>
                    <label className="block text-sm font-medium mb-1">AI Temperature</label>
                    <Input type="range" min="0" max="1" step="0.1" defaultValue="0.7" />
                </div>
                <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Fallback to OpenAI</label>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                    </label>
                </div>
            </div>
             <div className="mt-8 flex justify-end">
                <Button>Save Changes</Button>
            </div>
        </Card>
    </div>
);

const AuditLogViewer = () => (
    <div className="p-4 md:p-8">
        <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Audit Log Viewer</h1>
            <div className="flex gap-2">
                <Input type="date" className="w-auto" />
                <Button variant="outline">Export JSON</Button>
            </div>
        </div>
        <Card>
            <table className="w-full text-left font-mono text-sm">
                <thead>
                    <tr className="border-b dark:border-gray-700">
                        <th className="p-3">Timestamp</th>
                        <th className="p-3">User</th>
                        <th className="p-3">Action</th>
                        <th className="p-3">Target</th>
                    </tr>
                </thead>
                <tbody>
                    {MOCK_AUDIT_LOGS.map(log => (
                        <tr key={log.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                            <td className="p-3 text-gray-400">{new Date(log.timestamp).toISOString()}</td>
                            <td className="p-3">{log.user}</td>
                            <td className="p-3 text-yellow-400">{log.action}</td>
                            <td className="p-3">{log.target}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </Card>
    </div>
);

// Fallback for missing pages
const PlaceholderPage = ({ title }) => (
    <div className="p-4 md:p-8">
        <h1 className="text-3xl font-bold">{title}</h1>
        <Card className="mt-6">
            <p>This is a placeholder for the {title} page. Full implementation is pending.</p>
        </Card>
    </div>
);


// Main App Structure
const NavItem = ({ icon, label, active, onClick, children }) => {
    const [isOpen, setIsOpen] = useState(active);
    
    useEffect(() => {
        if(active) setIsOpen(true);
    }, [active]);

    const hasChildren = children && React.Children.count(children) > 0;

    return (
        <li>
            <a
                href="#"
                onClick={(e) => { e.preventDefault(); if(hasChildren) setIsOpen(!isOpen); else onClick(); }}
                className={`flex items-center p-2 text-base font-normal rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 ${active && !hasChildren ? 'bg-blue-100 dark:bg-blue-900 text-blue-600' : 'text-gray-900 dark:text-white'}`}
            >
                {icon}
                <span className="flex-1 ml-3 whitespace-nowrap">{label}</span>
                {hasChildren && <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />}
            </a>
            {hasChildren && isOpen && (
                <ul className="pl-6 mt-1 space-y-1">
                    {children}
                </ul>
            )}
        </li>
    );
}

const NavSubItem = ({ label, active, onClick }) => (
    <li>
        <a href="#" onClick={(e) => { e.preventDefault(); onClick(); }} className={`block p-2 text-sm rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 ${active ? 'bg-blue-100 dark:bg-blue-900 text-blue-600' : 'text-gray-900 dark:text-white'}`}>
            {label}
        </a>
    </li>
)


const App = () => {
    const [activePage, setActivePage] = useState('dashboard');
    const [isSidebarOpen, setSidebarOpen] = useState(true);
    const [isAiPanelOpen, setAiPanelOpen] = useState(false);
    const [isNotificationsOpen, setNotificationsOpen] = useState(false);

    const PageComponent = {
        'onboarding': OnboardingWizard,
        'dashboard': ComplianceDashboard,
        'policies': PolicyWorkspace,
        'planner': ImplementationPlanner,
        'evidence': EvidenceRepository,
        'integrations': IntegrationsHub,
        'assessments': () => <PlaceholderPage title="Assessment Sessions" />,
        'gap-analysis': ReadinessGapAnalysis,
        'reports': ReportCenter,
        'team': TeamManagement,
        'settings': SettingsPage,
        'audit-log': AuditLogViewer,
        'system-health': () => <PlaceholderPage title="System Health Monitor" />,
    }[activePage];

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
            {/* Sidebar */}
            <aside className={`transition-all duration-300 ${isSidebarOpen ? 'w-64' : 'w-0'} overflow-hidden bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex-shrink-0`}>
                <div className="flex items-center justify-between h-16 px-4 border-b dark:border-gray-700">
                    <span className="text-xl font-bold flex items-center"><Shield className="mr-2 text-blue-600"/>ComplyCo</span>
                </div>
                <div className="p-4">
                    <ul className="space-y-2">
                        <NavItem icon={<GanttChartSquare size={20} />} label="Onboarding" onClick={() => setActivePage('onboarding')} active={activePage === 'onboarding'}/>
                        <NavItem icon={<BarChart size={20} />} label="Dashboard" onClick={() => setActivePage('dashboard')} active={activePage === 'dashboard'}/>
                        <NavItem icon={<HardDrive size={20}/>} label="Compliance" active={['policies', 'gap-analysis', 'assessments'].includes(activePage)}>
                            <NavSubItem label="Policy Workspace" onClick={() => setActivePage('policies')} active={activePage === 'policies'}/>
                            <NavSubItem label="Gap Analysis" onClick={() => setActivePage('gap-analysis')} active={activePage === 'gap-analysis'}/>
                            <NavSubItem label="Assessments" onClick={() => setActivePage('assessments')} active={activePage === 'assessments'}/>
                        </NavItem>
                        <NavItem icon={<ClipboardCheck size={20}/>} label="Implementation" active={['planner', 'evidence'].includes(activePage)}>
                           <NavSubItem label="Planner" onClick={() => setActivePage('planner')} active={activePage === 'planner'}/>
                           <NavSubItem label="Evidence Repository" onClick={() => setActivePage('evidence')} active={activePage === 'evidence'}/>
                        </NavItem>
                        <NavItem icon={<GitBranch size={20}/>} label="Integrations" onClick={() => setActivePage('integrations')} active={activePage === 'integrations'}/>
                        <NavItem icon={<FileText size={20}/>} label="Reports" onClick={() => setActivePage('reports')} active={activePage === 'reports'}/>
                    </ul>
                     <ul className="pt-4 mt-4 space-y-2 border-t border-gray-200 dark:border-gray-700">
                        <NavItem icon={<User size={20}/>} label="Team Management" onClick={() => setActivePage('team')} active={activePage === 'team'}/>
                        <NavItem icon={<Settings size={20}/>} label="Settings" onClick={() => setActivePage('settings')} active={activePage === 'settings'}/>
                        <NavItem icon={<History size={20}/>} label="Audit Log" onClick={() => setActivePage('audit-log')} active={activePage === 'audit-log'}/>
                        <NavItem icon={<Briefcase size={20}/>} label="System Health" onClick={() => setActivePage('system-health')} active={activePage === 'system-health'}/>
                    </ul>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="flex justify-between items-center h-16 px-6 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
                    <div className="flex items-center gap-4">
                       <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
                            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                        </button>
                        <div className="relative">
                            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                            <Input className="pl-10 w-64" placeholder="Search controls, evidence..." />
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <Button variant="outline" onClick={() => setAiPanelOpen(true)}>
                            <Bot size={16} className="mr-2"/> AI Assistant
                        </Button>
                        <DropdownMenu trigger={
                            <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 relative">
                                <Bell size={20}/>
                                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-gray-800"></span>
                            </button>
                        }>
                            <div className="p-2 font-semibold border-b">Notifications</div>
                            {MOCK_NOTIFICATIONS.map(n => (
                                <DropdownMenuItem key={n.id}>
                                    <div className="flex gap-2">
                                        {n.type === 'Alert' && <AlertTriangle className="text-red-500 w-5 h-5"/>}
                                        {n.type !== 'Alert' && <CheckCircle className="text-blue-500 w-5 h-5"/>}
                                        <div>
                                            <p className="text-sm">{n.message}</p>
                                            <p className="text-xs text-gray-400">{n.time}</p>
                                        </div>
                                    </div>
                                </DropdownMenuItem>
                            ))}
                        </DropdownMenu>
                         <DropdownMenu trigger={
                            <div className="flex items-center gap-2 cursor-pointer">
                                <img src="https://placehold.co/32x32/E0E7FF/4338CA?text=A" alt="Admin User" className="w-8 h-8 rounded-full"/>
                                <div>
                                    <p className="text-sm font-semibold">Admin User</p>
                                    <p className="text-xs text-gray-500">Owner</p>
                                </div>
                                <ChevronDown size={16} />
                            </div>
                        }>
                            <DropdownMenuItem><LifeBuoy size={16} className="inline mr-2"/> Help</DropdownMenuItem>
                            <DropdownMenuItem><LogOut size={16} className="inline mr-2"/> Logout</DropdownMenuItem>
                        </DropdownMenu>
                    </div>
                </header>
                {/* Page content */}
                <main className="flex-1 overflow-y-auto">
                    <PageComponent />
                </main>
            </div>
            
             {/* AI Assistant Panel */}
            <Sheet isOpen={isAiPanelOpen} onClose={() => setAiPanelOpen(false)} side="right">
                <div className="flex flex-col h-full">
                    <div className="p-4 border-b dark:border-gray-700 flex justify-between items-center">
                        <h3 className="font-semibold flex items-center"><Bot className="mr-2"/> AI Assistant</h3>
                        <button onClick={() => setAiPanelOpen(false)}><X size={20}/></button>
                    </div>
                    <div className="flex-grow p-4 space-y-4 overflow-y-auto">
                        {/* Chat messages */}
                        <div className="flex gap-2">
                            <Bot className="w-6 h-6 flex-shrink-0"/>
                            <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                                <p>Hello! I'm your compliance copilot. How can I help you? You can use commands like <code className="bg-gray-200 dark:bg-gray-600 px-1 rounded">/generate-policy</code>.</p>
                            </div>
                        </div>
                         <div className="flex justify-end gap-2">
                            <div className="p-3 bg-blue-600 text-white rounded-lg">
                                <p>/generate-policy for Acceptable Use</p>
                            </div>
                            <User className="w-6 h-6 flex-shrink-0"/>
                        </div>
                    </div>
                    <div className="p-4 border-t dark:border-gray-700">
                        <div className="relative">
                            <Input className="pr-10" placeholder="Ask me anything..."/>
                            <button className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-blue-600">
                                <Send size={20}/>
                            </button>
                        </div>
                    </div>
                </div>
            </Sheet>
        </div>
    );
};

export default App;
