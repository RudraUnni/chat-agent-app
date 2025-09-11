# OpenRouter Integration Guide - COMPLETE SOLUTION

This document explains the comprehensive OpenRouter integration solution that resolves all compatibility issues with the `openai-agents` library.

## Problems Solved ✅

### 1. **AttributeError: 'str' object has no attribute 'output'**
- **Root Cause**: The `openai-agents` library expected OpenAI's response format with `.output` attributes
- **Solution**: Created comprehensive compatibility layer that wraps all responses with required attributes

### 2. **Monkey Patching Failures**
- **Root Cause**: `openai.AsyncOpenAI.chat.completions` is a cached property that can't be directly patched
- **Solution**: Implemented proper method replacement at the class level instead of property level

### 3. **OpenRouter API Key Authentication Issues**  
- **Root Cause**: Incorrect API key format or placeholder values
- **Solution**: Added comprehensive API key validation and automatic environment variable mapping

### 4. **Response Format Incompatibility**
- **Root Cause**: OpenRouter returns different response structures than expected by agents library
- **Solution**: Multi-strategy response handling with fallback mechanisms

## Solution Overview

Our solution implements a comprehensive compatibility layer that:

1. **Environment Variable Mapping**: Maps OpenRouter credentials to OpenAI environment variables for library compatibility
2. **Response Monkey Patching**: Patches the OpenAI client to ensure responses have expected attributes
3. **Agents Library Patching**: Patches the agents library's `run` method to handle different response types
4. **Robust Response Handling**: Implements fallback logic to handle various response formats

## Key Components

### 1. Environment Configuration

The system automatically maps OpenRouter credentials to OpenAI environment variables:

```bash
# Your OpenRouter credentials
OPENROUTER_API_KEY=sk-or-v1-your-actual-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Automatically mapped for agents library compatibility
OPENAI_API_KEY=sk-or-v1-your-actual-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Response Compatibility Layer

The `OpenRouterResponseAdapter` class:
- Patches the OpenAI client to add missing `output` attributes
- Creates compatible response objects when needed
- Handles both OpenAI and OpenRouter response formats

### 3. Agent Class Enhancements

The enhanced `Agent` class:
- Uses the original `openai-agents` library with compatibility patches
- Implements robust response handling for different response types
- Provides fallback to custom OpenRouter runner if needed
- Maintains full backward compatibility

### 4. Response Handling Logic

The system handles multiple response formats:
- Objects with `final_output` attribute
- Objects with `output` attribute  
- Plain strings
- OpenAI-style responses with `choices[0].message.content`
- Custom response objects

## Usage

### Basic Setup

1. Set your OpenRouter API key in `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-openrouter-key-here
```

2. Start the application:
```bash
docker-compose up -d
```

### Using in Code

The agents work exactly as before, but now use OpenRouter:

```python
from app.workflows.medical.runtime import Agent

# Create agent (automatically uses OpenRouter)
agent = Agent(
    name="Medical Agent",
    instructions="You are a medical research assistant",
    model="openai/gpt-4o-mini"
)

# Use agent (handles OpenRouter responses automatically)
result = await agent.invoke("What are the latest diabetes treatments?")
```

### Multi-Agent Workflows

The existing multi-agent workflows work without changes:

```python
from app.workflows.medical.agents import orchestrate

# This now uses OpenRouter for all agents
response = await orchestrate(
    "Find recent papers about diabetes treatment", 
    conversation_history=[]
)
```

## Error Handling

The system includes comprehensive error handling:

1. **API Errors**: OpenRouter API errors are caught and returned as error responses
2. **Response Format Issues**: Automatic fallback to custom response handling
3. **Missing Attributes**: Automatic addition of required attributes to responses
4. **Library Compatibility**: Monkey patches ensure library compatibility

## Testing

The integration includes built-in compatibility testing:
- Environment variable setup verification
- Response wrapper class testing
- Response handling logic verification
- Monkey patch application testing

## Troubleshooting

### Common Issues

1. **"OPENROUTER_API_KEY not found"**
   - Ensure your `.env` file has the correct API key
   - Check Docker environment variable mapping

2. **"AttributeError: 'str' object has no attribute 'output'"**
   - This should be fixed by the compatibility layer
   - Check that monkey patches are applied correctly

3. **API Key Errors**
   - Verify your OpenRouter API key is valid
   - Ensure the key has sufficient credits/permissions

### Debug Mode

Enable debug logging by setting:
```bash
DEBUG=true
```

This will show:
- Environment variable setup messages
- Monkey patch application status
- Response handling debug information

## Production Deployment

For production deployment:

1. Set environment variables in `docker-compose.yml`
2. Ensure OpenRouter API key is properly secured
3. Monitor API usage and costs
4. Set appropriate rate limits

## Model Configuration

You can use any OpenRouter-supported model:

```python
agent = Agent(
    name="Agent",
    instructions="Instructions",
    model="anthropic/claude-3-sonnet"  # Any OpenRouter model
)
```

Popular models:
- `openai/gpt-4o-mini` (recommended for cost efficiency)
- `openai/gpt-4o`
- `anthropic/claude-3-sonnet`
- `anthropic/claude-3-haiku`

## Support

If you encounter issues:
1. Check the debug logs for error messages
2. Verify environment variable setup
3. Test with a simple agent first
4. Check OpenRouter API status and credits