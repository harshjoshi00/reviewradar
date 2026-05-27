# 🚀 Deploying ReviewRadar to Production (Render + Vercel)

Follow these step-by-step instructions to deploy your web application online for free.

---

## Step 1: Push Your Code to GitHub

Since Render and Vercel build directly from GitHub, you first need to publish your code there.

1. **Initialize Git** in the project root directory:
   ```bash
   git init
   ```
2. **Commit all files** (the root `.gitignore` will automatically prevent sending large files like `venv`, `node_modules`, and raw `Dataset`):
   ```bash
   git add .
   git commit -m "Setup ReviewRadar for production deployment"
   ```
3. **Create a new, empty repository** on [GitHub](https://github.com/new).
4. **Push your code** to your new repository (replace `<your-github-repo-url>` with your actual URL):
   ```bash
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

---

## Step 2: Deploy the Backend to Render (Free)

[Render](https://render.com/) will host your FastAPI backend and run predictions using your trained model.

1. Go to [Render](https://render.com) and sign in/create a free account.
2. Click **New +** (top right) and choose **Web Service**.
3. Connect your GitHub account and select your **ReviewRadar** repository.
4. Fill in the deployment details:
   - **Name**: `reviewradar-api` (or any name you prefer)
   - **Region**: Choose the region closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend` (⚠️ **CRITICAL: This tells Render to run within the backend folder**)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Click **Deploy Web Service**.
6. Render will install your packages and boot up the FastAPI server.
7. Once deployed, copy your **Web Service URL** from the top left corner (e.g. `https://reviewradar-api.onrender.com`).

---

## Step 3: Deploy the Frontend to Vercel (Free)

[Vercel](https://vercel.com/) will host your React frontend on a super-fast, global CDN.

1. Go to [Vercel](https://vercel.com) and sign in/create a free account.
2. Click **Add New...** (top right) and select **Project**.
3. Import your **ReviewRadar** repository from your connected GitHub account.
4. Configure the project settings:
   - **Framework Preset**: `Vite` (automatically detected)
   - **Root Directory**: Click *Edit* and select **`frontend`** (⚠️ **CRITICAL: This tells Vercel to build the React application inside the frontend folder**)
   - **Build & Development Settings**: Keep defaults (`npm run build` outputs to `dist`)
   - **Environment Variables**:
     - **Key**: `VITE_API_URL`
     - **Value**: Enter your Render backend URL (e.g. `https://reviewradar-api.onrender.com`)
     - *Note: Do not include a trailing slash `/` at the end of the URL.*
5. Click **Deploy**.
6. Vercel will build your assets in ~1 minute and give you a live production URL (e.g. `https://reviewradar-frontend.vercel.app`).

---

## 💡 Pro Tips

* **Render Cold Starts**: Because Render's Web Service is on the free tier, it will "sleep" after 15 minutes of inactivity. The first request after a sleep period can take 30–50 seconds to boot up. Once active, it responds instantly.
* **Updating the App**: Any time you commit and push new changes to GitHub (`git push`), Render and Vercel will automatically rebuild and deploy the new version!
