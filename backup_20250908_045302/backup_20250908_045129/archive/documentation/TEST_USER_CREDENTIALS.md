# 🔑 Test User Credentials for RuleIQ Development

This document contains the test user credentials for easy development and testing.

## 🚀 Quick Login

**Frontend URL:** http://localhost:3000/login

**Test User Credentials:**
- **📧 Email:** `test@ruleiq.dev`
- **🔒 Password:** `TestPassword123!`

## 🛠️ Management Scripts

### Create Test User
```bash
python scripts/create_test_user.py
```

### Test Login (API)
```bash
python scripts/create_test_user.py --test
```

### Help
```bash
python scripts/create_test_user.py --help
```

## 🔄 Development Workflow

1. **Start Backend:**
   ```bash
   python main.py
   ```

2. **Start Frontend:**
   ```bash
   cd Frontend
   npm run dev
   ```

3. **Login to Frontend:**
   - Go to http://localhost:3000/login
   - Use the test credentials above
   - You'll be redirected to the dashboard

## 📋 Available Features

After logging in with the test user, you can access:

- ✅ **Dashboard** - Main overview page
- ✅ **Business Profile** - Company information management
- 🚧 **Assessment Workflow** - Coming next
- 🚧 **Compliance Frameworks** - Coming next
- 🚧 **Reports & Analytics** - Coming next

## ⚠️ Important Notes

- **DO NOT USE IN PRODUCTION** - These are development credentials only
- The test user is automatically created when you run the script
- If the user already exists, the script will just display the credentials
- The backend must be running for the script to work

## 🔧 Troubleshooting

### Backend Not Running
If you get a connection error:
```bash
# Start the backend first
python main.py
```

### Frontend Not Running
If the frontend is not accessible:
```bash
cd Frontend
npm run dev
```

### Database Issues
If you encounter database errors:
```bash
# Reinitialize the database
python database/init_db.py
```

## 🎯 Next Steps

With the test user set up, you can now:

1. **Test the Business Profile Form** - Navigate to `/business-profile`
2. **Develop New Features** - Use the test user for authentication
3. **Run Tests** - The test user works with the existing test suite
4. **Demo the Application** - Show features to stakeholders

---

**Happy Coding! 🚀**
