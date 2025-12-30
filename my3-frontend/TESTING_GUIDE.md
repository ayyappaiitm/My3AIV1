# Frontend Testing Guide

This guide shows you how to test the My3 frontend dashboard.

## Prerequisites

1. **Backend server must be running:**
   ```bash
   cd my3-backend
   python -m uvicorn app.main:app --reload
   ```
   Backend should be at: `http://localhost:8000`

2. **Database must be running:**
   ```bash
   cd my3-backend
   docker-compose up -d
   ```

## Step 1: Install Dependencies (if not already done)

```bash
cd my3-frontend
npm install
```

## Step 2: Set Up Environment Variables

Create a `.env.local` file in `my3-frontend/`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Or the API client will default to `http://localhost:8000`.

## Step 3: Start the Frontend Server

```bash
cd my3-frontend
npm run dev
```

The frontend will start at: `http://localhost:3000`

## Step 4: Test the Dashboard

### 4.1: Login/Register

1. **Open browser:** `http://localhost:3000`
2. **Register a new account:**
   - Go to `/register`
   - Fill in: Name, Email, Password (min 8 chars)
   - Click "Sign Up"
   - Should redirect to `/dashboard`

3. **Or login:**
   - Go to `/login`
   - Use credentials from backend test
   - Should redirect to `/dashboard`

### 4.2: Test Dashboard Layout

**What to check:**

1. **Header:**
   - ✅ Logo "My3" visible (top left)
   - ✅ Search bar visible (center, disabled)
   - ✅ Profile dropdown (top right) with user name/avatar
   - ✅ Click profile → Shows dropdown with Settings and Logout
   - ✅ Click Logout → Redirects to login

2. **Network Graph:**
   - ✅ Graph visible in background
   - ✅ If no recipients: Graph is empty (no nodes)
   - ✅ Graph opacity is 0.6 (semi-transparent)

3. **Chat Window:**
   - ✅ Centered on screen
   - ✅ Frosted glass effect (backdrop blur visible)
   - ✅ Size: 600px × 700px (on desktop)
   - ✅ Shows "Hello! I'm My3" message when empty
   - ✅ Chat input at bottom

### 4.3: Test Chat Functionality

1. **Send a message:**
   - Type: "My mom loves gardening, her birthday is April 16"
   - Click Send or press Enter
   - ✅ User message appears immediately
   - ✅ Graph opacity fades to 0.2 (when typing/loading)
   - ✅ AI response appears after loading
   - ✅ Graph opacity returns to 0.6

2. **Test confirmation flow:**
   - If AI asks to add a recipient
   - ✅ Confirmation prompt appears
   - ✅ Yes/No buttons visible (if ConfirmationPrompt component exists)

3. **Test recipient creation:**
   - After confirming, recipient should be added
   - ✅ New node appears in graph
   - ✅ Node shows initials (e.g., "MO" for Mom)
   - ✅ Node color based on relationship (family = red, etc.)

### 4.4: Test Network Graph Interactions

1. **Click a node:**
   - ✅ Node becomes highlighted (opacity 1.0)
   - ✅ Chat input pre-fills with "Gift ideas for [Name]"
   - ✅ Input is focused automatically

2. **Hover a node:**
   - ✅ Node scales up slightly (r: 40 → 45)
   - ✅ Opacity increases to 1.0

3. **Graph opacity during typing:**
   - ✅ Start typing in chat input
   - ✅ Graph fades to 0.2 opacity
   - ✅ Smooth transition (300ms)

### 4.5: Test Responsive Design

1. **Desktop (1920px+):**
   - ✅ Chat window: 600px × 700px
   - ✅ Graph visible in background
   - ✅ Header full width

2. **Tablet (768px - 1024px):**
   - ✅ Chat window: Max 600px width, responsive height
   - ✅ Graph still visible
   - ✅ Header adapts

3. **Mobile (< 768px):**
   - ✅ Chat window: Full width minus padding
   - ✅ Height: 600px (reduced)
   - ✅ Graph may be hidden or in drawer (if implemented)

## Step 5: Test Error Handling

1. **Backend not running:**
   - Stop backend server
   - Try to send a message
   - ✅ Error message appears
   - ✅ UI doesn't crash

2. **Invalid credentials:**
   - Try to login with wrong password
   - ✅ Error message appears
   - ✅ Doesn't redirect

3. **Network error:**
   - Disconnect internet
   - Try to send message
   - ✅ Error handling works
   - ✅ User-friendly error message

## Step 6: Test Multiple Recipients

1. **Add multiple recipients:**
   - "My mom loves gardening"
   - "My dad likes tech gadgets"
   - "My wife's birthday is June 5"
   - "My friend Sarah loves yoga"

2. **Verify graph:**
   - ✅ All nodes appear in graph
   - ✅ Nodes spread around chat window
   - ✅ No overlapping
   - ✅ Color coding works (family = red, spouse = coral, friend = teal)

3. **Test max 10 limit:**
   - Add 10 recipients
   - Try to add 11th
   - ✅ Error message: "Maximum 10 recipients allowed"

## Quick Test Checklist

- [ ] Frontend starts without errors
- [ ] Can register new user
- [ ] Can login
- [ ] Dashboard loads after login
- [ ] Header visible with logo and profile
- [ ] Chat window centered with frosted glass
- [ ] Can send messages
- [ ] Graph opacity changes when typing
- [ ] Can click graph nodes
- [ ] Chat pre-fills when node clicked
- [ ] Recipients appear in graph after adding
- [ ] Responsive on mobile
- [ ] Logout works

## Troubleshooting

### Frontend won't start:
```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Or use different port
PORT=3001 npm run dev
```

### API connection errors:
- Verify backend is running: `http://localhost:8000/api/health`
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check browser console for CORS errors

### Graph not showing:
- Check browser console for D3.js errors
- Verify recipients are being fetched
- Check Network tab for API calls

### Styling issues:
- Clear `.next` cache: `rm -rf .next` (or delete folder on Windows)
- Restart dev server
- Check Tailwind is compiling: Look for CSS in browser dev tools

### Authentication issues:
- Check `localStorage` in browser dev tools for `auth_token`
- Verify token is being sent in API requests (Network tab)
- Check backend logs for auth errors

## Next Steps

Once basic testing passes:
1. Test with real OpenAI API key (for actual LLM responses)
2. Test confirmation flows
3. Test gift idea display (if GiftInlineCard component exists)
4. Test occasion tracking
5. Performance testing (many recipients, long conversations)


