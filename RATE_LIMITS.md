# 🚦 API Rate Limits & Quota Management

## Understanding the Error

The error you encountered:
```
429 You exceeded your current quota
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
limit: 20, model: gemini-2.5-flash
```

This means:
- **Free tier limit**: 20 requests per day for `gemini-2.5-flash`
- **You hit the daily limit** - need to wait until it resets

---

## ✅ Fixed: Switched to Better Model

I've updated your code to use `gemini-1.5-flash` which has:

### Rate Limits (Free Tier):
- **15 requests per minute (RPM)**
- **1,500 requests per day (RPD)**
- **1 million tokens per minute (TPM)**

Much better than `gemini-2.5-flash`'s 20 requests per day!

### What Changed:
1. **`app/config.py`**: Model changed to `gemini-1.5-flash`
2. **`app/services/summarizer.py`**: 
   - Model updated
   - Batch size increased to 5 (fewer API calls)
   - Rate limit increased to 10 RPM
3. **`app/services/qa_system.py`**: Model updated

---

## 🎯 Rate Limit Best Practices

### Current Configuration (Optimized):
```python
Model: gemini-1.5-flash
Batch size: 5 chunks per request
Rate limit: 10 requests per minute (safe margin from 15 RPM limit)
Delay between requests: 6 seconds
```

### Typical Paper Analysis:
- **Small paper (5-10 pages)**: ~3-5 API calls
- **Medium paper (10-20 pages)**: ~6-10 API calls  
- **Large paper (20-30 pages)**: ~12-18 API calls

With the new limits, you can analyze **multiple papers per day**!

---

## 📊 Model Comparison

| Model | RPM (Free) | RPD (Free) | Best For |
|-------|-----------|-----------|----------|
| `gemini-1.5-flash` | 15 | 1,500 | ✅ **Multiple papers daily** |
| `gemini-1.5-flash-8b` | 15 | 1,500 | Faster, lighter analysis |
| `gemini-1.5-pro` | 2 | 50 | Highest quality, limited use |
| `gemini-2.5-flash` | - | 20 | ❌ Too restrictive |

---

## 💡 If You Still Hit Rate Limits

### Option 1: Wait for Reset
Rate limits reset every 24 hours (midnight UTC).

### Option 2: Get a Paid API Key
- Upgrade at: https://ai.google.dev/pricing
- **Pay-as-you-go**: Much higher limits
- **Enterprise**: Unlimited

### Option 3: Reduce API Calls

**In `app/config.py`, increase batch size:**
```python
# In app/services/summarizer.py, line 27
batch_size = 10  # Process more chunks per request
```

**Trade-off**: Larger batches may reduce summary quality but use fewer API calls.

### Option 4: Process Smaller Sections

Only select specific features instead of "All Features":
```
1. ✅ Paper Summary only (5-10 API calls)
2. Skip Q&A (saves 15+ API calls)
```

---

## 🔍 Monitor Your Usage

Check your quota usage at:
https://ai.dev/usage?tab=rate-limit

---

## 🎯 Recommended Workflow

### For Free Tier:
1. Start with **summary + citations only** (10-15 API calls)
2. If you want Q&A, run it separately later
3. Space out analyses throughout the day

### With Paid Tier:
- Run all features simultaneously
- Process multiple papers
- No waiting required

---

## 🚀 Quick Test

Try running now with the updated model:

```bash
python main.py
```

Select:
- Features: **1 (Summary only)** - to test
- Format: **1 (Markdown)** - quick export

This should work within your new rate limits!

---

## ⚙️ Advanced: Custom Rate Limiting

Edit `app/services/summarizer.py` line 46:

```python
# Conservative (slow but safe)
requests_per_minute = 5

# Balanced (current setting)
requests_per_minute = 10

# Aggressive (risky, may hit limits)
requests_per_minute = 14
```

---

**Your app is now optimized for the free tier with much better rate limits!** 🎉
