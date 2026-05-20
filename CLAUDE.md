# PPT Generator

A Python CLI tool that auto-generates PowerPoint presentations from topics using Claude AI.

## Quick Start

```bash
python3 generate.py "AI 트렌드 2026" --slides 8 --output ai_trends.pptx
```

**Requirements:**
- `ANTHROPIC_API_KEY` environment variable, OR
- `--api-key` flag with your API key

## Setup

```bash
pip install -r requirements.txt
```

## Project Structure

- `generate.py` — Main CLI script (342 lines)
- `requirements.txt` — Python dependencies

## Key Implementation Details

### Claude Integration
- Model: `claude-opus-4-7`
- Prompt caching on system prompt for efficiency
- JSON-structured slide generation with theme colors

### python-pptx Features
- 16:9 widescreen slides (13.33" × 7.5")
- Slide types:
  - Title slide (auto-generated)
  - Table of contents (auto-generated)
  - Section dividers
  - Content (bullets, two-column, quote layouts)
  - Closing slide (auto-generated)
- Theme colors: primary, accent, text_on_dark, text_on_light

### CLI Options
- `topic` (positional) — Presentation topic
- `--slides N` — Number of content slides (default: 8)
- `--output FILE` — Output PPTX path (default: output.pptx)
- `--api-key KEY` — Anthropic API key (overrides env var)

## Development Workflow

1. **Local Testing:**
   - Set `ANTHROPIC_API_KEY` or pass `--api-key`
   - Run `python3 generate.py` with test topic
   - Verify output PPTX structure and rendering

2. **Code Changes:**
   - Modify `generate.py` or prompt in `SYSTEM_PROMPT`
   - Test locally before committing
   - Validate JSON parsing and slide rendering

3. **Git Workflow:**
   - Commit changes with descriptive messages
   - Push to `origin/master`

## Future Enhancements

- Template customization (colors, fonts)
- Export to other formats (PDF, ODP)
- Batch processing multiple topics
- Custom slide layouts
- Speaker notes support
