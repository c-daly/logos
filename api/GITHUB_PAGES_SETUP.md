# GitHub Pages Setup Guide for API Documentation

This guide walks through the steps to enable GitHub Pages for the LOGOS API documentation.

## Automated Setup (Recommended)

The repository is now configured with a fully automated GitHub Actions workflow that deploys to the `gh-pages` branch. This approach requires minimal configuration and handles everything automatically.

### Steps:

1. **Merge the PR to `main`**:
   - Once this PR is merged, the workflow will automatically run

2. **Enable GitHub Pages (one-time setup)**:
   - Go to the repository on GitHub
   - Navigate to **Settings** → **Pages**
   - Under "Build and deployment":
     - **Source**: Select "Deploy from a branch"
     - **Branch**: Select `gh-pages`
     - **Folder**: Select `/ (root)`
   - Click **Save**
   
   **Note**: The `gh-pages` branch will be automatically created by the workflow on first run.

3. **Access the Documentation**:
   - After the workflow completes and Pages is enabled, the documentation will be available at:
     - Main Index: `https://c-daly.github.io/logos/api/`
     - Hermes API: `https://c-daly.github.io/logos/api/hermes.html`

### How It Works

The workflow automatically:
1. Generates API documentation from OpenAPI specs in `contracts/`
2. Pushes the generated docs to the `gh-pages` branch
3. GitHub Pages serves the content from the `gh-pages` branch

Future updates happen automatically whenever:
- OpenAPI specs in `contracts/` are modified
- The generation script is updated
- Changes are pushed to `main`

## Manual Deployment (Alternative)

If you prefer to deploy without the automated workflow:

### Steps:

1. **Generate documentation locally**:
   ```bash
   ./scripts/generate-api-docs.sh
   ```

2. **Commit and push**:
   ```bash
   git add docs/api/
   git commit -m "Update API documentation"
   git push origin main
   ```

3. **Enable GitHub Pages from main branch**:
   - Go to **Settings** → **Pages**
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs`
   - Click **Save**

4. **Access**: `https://c-daly.github.io/logos/api/`

## Verifying the Setup

After enabling GitHub Pages:

1. **Check Deployment Status**:
   - Go to **Settings** → **Pages**
   - You should see: "Your site is live at https://c-daly.github.io/logos/"

2. **Verify the Documentation**:
   - Visit: `https://c-daly.github.io/logos/api/`
   - You should see the LOGOS API Documentation landing page
   - Click on "Hermes API" to verify the API documentation loads correctly

3. **Monitor GitHub Actions** (if using GitHub Actions deployment):
   - Go to **Actions** tab
   - Check the "Publish API Documentation" workflow
   - Ensure it completes successfully

## Troubleshooting

### Documentation Not Appearing

If the documentation doesn't appear after enabling GitHub Pages:

1. **Check the workflow**:
   - Go to **Actions** tab
   - Look for "Publish API Documentation" workflow runs
   - Ensure it completed successfully
   - Check for any errors in the logs

2. **Verify gh-pages branch**:
   - Check if the `gh-pages` branch exists
   - Verify it contains the documentation files in the root directory
   - The workflow creates this branch automatically on first run

3. **Check Pages settings**:
   - Go to **Settings** → **Pages**
   - Ensure source is set to "Deploy from a branch"
   - Ensure branch is set to `gh-pages` (not `main`)
   - Ensure folder is set to `/ (root)` (not `/docs`)

4. **Check the URL**:
   - The API docs are at: `https://c-daly.github.io/logos/api/`
   - Not at: `https://c-daly.github.io/logos/docs/api/`

5. **Wait for propagation**:
   - First deployment can take 5-10 minutes
   - Try clearing your browser cache or using an incognito window

### Workflow Failing

If the "Publish API Documentation" workflow fails:

1. **Check permissions**:
   - Go to **Settings** → **Actions** → **General**
   - Scroll to "Workflow permissions"
   - Ensure "Read and write permissions" is enabled
   - This allows the workflow to create/update the `gh-pages` branch

2. **Check the error logs**:
   - Go to **Actions** → Find the failed run
   - Click on the job that failed
   - Review the error message and logs

3. **Common issues**:
   - **Pages not enabled**: Enable GitHub Pages first (see setup steps above)
   - **Permission denied**: Check workflow permissions in Settings
   - **Node.js errors**: The workflow uses Node.js 20, which should be available

### Custom Domain

If you want to use a custom domain:

1. Go to **Settings** → **Pages**
2. Under "Custom domain", enter your domain (e.g., `docs.logos.dev`)
3. Follow GitHub's instructions for DNS configuration
4. Wait for DNS propagation (can take 24-48 hours)

## Updating Documentation

### Automatic Updates (GitHub Actions)

If using GitHub Actions deployment:
- Documentation automatically rebuilds when you push changes to:
  - Any file in `contracts/` (e.g., updating `hermes.openapi.yaml`)
  - The generation script (`scripts/generate-api-docs.sh`)
  - The workflow file (`.github/workflows/publish-api-docs.yml`)

### Manual Updates (Deploy from Branch)

If deploying from the `main` branch `/docs` folder:

1. Make changes to OpenAPI specifications in `contracts/`
2. Run: `./scripts/generate-api-docs.sh`
3. Commit the changes: `git add docs/api/ && git commit -m "Update API docs"`
4. Push to `main`: `git push`
5. GitHub Pages will automatically redeploy

## Adding New API Documentation

When new API specifications are added (e.g., Sophia, Talos, Apollo):

1. Add the OpenAPI spec to `contracts/`:
   ```bash
   cp sophia.openapi.yaml contracts/
   ```

2. If using **GitHub Actions**:
   - Push the new spec to `main`
   - The workflow will automatically generate and deploy the new documentation

3. If using **Deploy from Branch**:
   - Run the generation script: `./scripts/generate-api-docs.sh`
   - Commit and push the changes

4. The new API will automatically appear on the index page

## Maintenance

### Keeping Redocly Up to Date

The documentation uses Redocly CLI via `npx`, which always fetches the latest version. No manual updates are needed.

### Monitoring

- Set up notifications for the "Publish API Documentation" workflow:
  - Go to **Actions** → **Publish API Documentation**
  - Click the "..." menu → **View workflow file**
  - Watch the repository to get notifications on workflow failures

## Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions for Pages](https://github.com/actions/deploy-pages)
- [Redocly CLI Documentation](https://redocly.com/docs/cli/)
- [OpenAPI 3.1.0 Specification](https://spec.openapis.org/oas/v3.1.0)

## Need Help?

If you encounter issues not covered in this guide:
1. Check the GitHub Actions logs for detailed error messages
2. Review the [LOGOS Contributing Guide](../../CONTRIBUTING.md)
3. Open an issue on GitHub with the "documentation" label
