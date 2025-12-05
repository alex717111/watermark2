# Test Output Directory

This directory contains test output files from the video watermark tool tests.

## Generated Files

### Test Source Files
- **test_video.mp4** (48 KB) - Original test video (3 seconds, 1280x720)
- **test_watermark.png** (11 KB) - Full-size watermark image (1280x720)
- **test_insert.mp4** (24 KB) - Insert video for testing (2 seconds)

### Output Results
- **output_watermark.mp4** (54 KB) - Result with image watermark
- **output_text.mp4** (55 KB) - Result with text watermark
- **output_insert.mp4** (112 KB) - Result with video inserted

## How to Verify

Play each .mp4 file to verify the effects:

```bash
# View image watermark result
ffplay output_watermark.mp4

# View text watermark result
ffplay output_text.mp4

# View video insertion result
ffplay output_insert.mp4
```

## Test Summary

All tests passed successfully:
- ✅ 5/5 unit tests passed
- ✅ Image watermark functional test passed
- ✅ Text watermark functional test passed
- ✅ Video insert functional test passed

Generated on: 2025-12-05
