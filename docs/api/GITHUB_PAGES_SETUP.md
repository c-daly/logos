# GitHub Pages Setup Guide for API Documentation

This guide walks through the steps to enable GitHub Pages for the LOGOS API documentation.

## Quick Setup (Recommended)

The repository is configured to use GitHub Actions to deploy to GitHub Pages. This is the recommended approach as it provides better control and allows for custom build steps.

### Steps:

1. **Enable GitHub Pages with GitHub Actions**:
   - Go to the repository on GitHub
   - Navigate to **Settings** → **Pages**
   - Under "Build and deployment":
     - **Source**: Select "GitHub Actions"
   - Click **Save**

2. **Trigger the Workflow**:
   - The workflow will automatically run on the next push to `main` that affects files in `contracts/` or the documentation scripts
   - Or manually trigger it:
     - Go to **Actions** → **Publish API Documentation**
     - Click **Run workflow** → **Run workflow**

3. **Access the Documentation**:
   - After the workflow completes, the documentation will be available at:
     - Main Index: `https://c-daly.github.io/logos/api/`
     - Hermes API: `https://c-daly.github.io/logos/api/hermes.html`

## Alternative Setup (Deploy from Branch)

If you prefer to deploy from a branch instead of using GitHub Actions:

### Steps:

1. **Enable GitHub Pages**:
   - Go to the repository on GitHub
   - Navigate to **Settings** → **Pages**
   - Under "Build and deployment":
     - **Source**: Select "Deploy from a branch"
     - **Branch**: Select `main`
     - **Folder**: Select `/docs`
   - Click **Save**

2. **Wait for Deployment**:
   - GitHub Pages will automatically deploy from the `docs/` directory
   - This may take a few minutes
   - The site will be available at: `https://c-daly.github.io/logos/api/`

3. **Note**: With this approach, you need to manually run `./scripts/generate-api-docs.sh` and commit the generated files before pushing to `main`.

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

1. **Check the deployment**:
   - Go to **Actions** tab
   - Look for "pages build and deployment" workflow runs
   - Check for any errors in the logs

2. **Verify files exist**:
   - Ensure `docs/api/index.html` and `docs/api/hermes.html` exist in the `main` branch
   - If using GitHub Actions deployment, check that the workflow completed successfully

3. **Check the URL**:
   - Make sure you're accessing the correct URL
   - The base URL is `https://<username>.github.io/<repo>/`
   - API docs are at `https://<username>.github.io/<repo>/api/`

4. **Wait for propagation**:
   - Sometimes it takes 5-10 minutes for GitHub Pages to update
   - Try clearing your browser cache or using an incognito window

### Workflow Failing

If the "Publish API Documentation" workflow fails:

1. **Check permissions**:
   - Go to **Settings** → **Actions** → **General**
   - Scroll to "Workflow permissions"
   - Ensure "Read and write permissions" is enabled
   - Check that "Allow GitHub Actions to create and approve pull requests" is enabled

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
