# Vercel Rollback Procedure

This document outlines the procedure for rolling back the frontend application to a previous production deployment using the `rollback.yml` GitHub Actions workflow.

## 1. When to Use This Procedure

This procedure should be used in critical situations where a recent production deployment has introduced a severe issue, such as:

- A site-wide outage.
- Critical functionality being broken (e.g., login, checkout).
- A major, user-facing bug that significantly degrades the user experience.

**Principle**: Prefer rolling forward with a hotfix if possible. A rollback is a last resort to quickly restore service.

## 2. How to Perform a Rollback

The rollback process is triggered manually via a GitHub Actions workflow. You will need a **Vercel Deployment ID** for the specific deployment you want to restore.

### Step 2.1: Find the Vercel Deployment ID

1.  Go to your project's dashboard on [Vercel](https://vercel.com/).
2.  Navigate to the **Deployments** tab.
3.  Filter the deployments by the **Production** environment.
4.  Identify the last known good deployment you want to restore. It will have a status of "Ready".
5.  Click on the deployment to view its details.
6.  The **Deployment ID** is the unique identifier for that deployment (e.g., `dpl_...`). You can also get it from the URL, which will look something like `https://vercel.com/YOUR_ORG/YOUR_PROJECT/dpl_...`.

### Step 2.2: Trigger the Rollback Workflow

1.  In the project's GitHub repository, go to the **Actions** tab.
2.  In the left sidebar, find and click on the **"Rollback Frontend"** workflow.
3.  You will see a message: "This workflow has a `workflow_dispatch` event trigger." Click the **"Run workflow"** button on the right.
4.  A dropdown will appear. In the **"Vercel Deployment ID to restore"** input field, paste the Deployment ID you copied from the Vercel dashboard.
5.  Click the **"Run workflow"** button.

### Step 2.3: Monitor and Verify the Rollback

1.  The workflow will start running. You can monitor its progress in the Actions tab.
2.  The workflow will use the Vercel CLI to "promote" the specified older deployment to become the new `production` deployment.
3.  Once the workflow completes successfully, the production URL (`https://ruleiq.com`) will instantly point to the restored deployment.
4.  **Verification**:
    - Clear your browser cache and visit the production URL.
    - Perform a quick smoke test to confirm that the critical issue is resolved and the site is stable.
    - Check the Vercel dashboard. You should see the old deployment you selected now has the "Production" tag.

## 3. Post-Rollback Actions

- **Communicate**: Inform the team and stakeholders that a rollback has been performed.
- **Investigate**: Create a high-priority ticket to investigate the root cause of the issue in the faulty deployment.
- **Plan**: Plan a proper hotfix to address the underlying bug so you can roll forward again.

---

This document serves as the official procedure. Performing these steps constitutes a test of the rollback process.
