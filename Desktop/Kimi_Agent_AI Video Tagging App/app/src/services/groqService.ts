import type { ContextQuestions, DescriptionAngle, HashtagSet, ThumbnailPrompt, Platform } from '@/types';

// Use fetch-based approach for Groq API
const callGroqAPI = async (messages: any[], temperature: number, maxTokens: number): Promise<string> => {
  const apiKey = import.meta.env.VITE_GROQ_API_KEY;
  
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-3.1-70b-versatile',
      messages,
      temperature,
      max_tokens: maxTokens,
      response_format: { type: 'json_object' },
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Failed to call Groq API');
  }

  const data = await response.json();
  return data.choices[0]?.message?.content;
};

export interface GenerateDescriptionsParams {
  transcript: string;
  context: ContextQuestions;
  platform: Platform;
}

export interface GenerateHashtagsParams {
  transcript: string;
  selectedDescription: string;
  context: ContextQuestions;
  platform: Platform;
}

export interface GenerateThumbnailsParams {
  transcript: string;
  selectedDescription: string;
  selectedHashtags: string[];
  context: ContextQuestions;
}

const generateDescriptionsPrompt = (params: GenerateDescriptionsParams): string => {
  const { transcript, context, platform } = params;
  
  return `You are an expert social media content strategist specializing in viral content optimization.

Analyze this video transcript and create 3 compelling descriptions from different strategic angles.

TRANSCRIPT:
"""${transcript}"""

CONTEXT:
- Tone: ${context.tone}
- Content Type: ${context.contentType}
- Platform: ${platform}

Create 3 descriptions with these angles:
1. CURIOSITY GAP - Creates intrigue, makes viewers need to know more
2. EMOTIONAL HOOK - Taps into strong emotions (relatable, shocking, inspiring)
3. VALUE PROMISE - Clearly states what the viewer will gain/learn

Each description should:
- Be optimized for ${platform} algorithm
- Include strategic line breaks for readability
- Be 100-300 characters for maximum engagement
- Use power words that drive clicks
- Match the ${context.tone} tone

Respond in JSON format:
{
  "descriptions": [
    {
      "id": "1",
      "angle": "Curiosity Gap",
      "description": "...",
      "reasoning": "Why this angle works..."
    },
    {
      "id": "2",
      "angle": "Emotional Hook",
      "description": "...",
      "reasoning": "Why this angle works..."
    },
    {
      "id": "3",
      "angle": "Value Promise",
      "description": "...",
      "reasoning": "Why this angle works..."
    }
  ]
}`;
};

const generateHashtagsPrompt = (params: GenerateHashtagsParams): string => {
  const { transcript, selectedDescription, context, platform } = params;
  
  return `You are a TikTok/Fanworlds hashtag optimization expert who understands platform algorithms.

Create 4 strategic hashtag sets based on this content:

SELECTED DESCRIPTION:
"""${selectedDescription}"""

TRANSCRIPT:
"""${transcript}"""

CONTEXT:
- Tone: ${context.tone}
- Content Type: ${context.contentType}
- Platform: ${platform}

Create 4 hashtag sets:

1. TRENDING SET - Mix of trending hashtags (1M+ posts) + niche tags
   Focus: Maximum discoverability through trending topics
   
2. NICHE DOMINATION - Highly specific hashtags (10K-500K posts)
   Focus: Own your niche, less competition, higher engagement rate
   
3. BROAD APPEAL - General viral hashtags (500K-5M posts)
   Focus: Cast wide net for mass appeal content
   
4. COMMUNITY BUILDING - Engagement-focused hashtags
   Focus: Build loyal following, encourage comments/shares

Each set should have 8-12 hashtags optimized for ${platform}.
Include estimated reach and engagement score (1-100).

Respond in JSON format:
{
  "hashtagSets": [
    {
      "id": "1",
      "category": "Trending Mix",
      "hashtags": ["#...", "#..."],
      "estimatedReach": "500K-2M",
      "engagementScore": 85
    },
    {
      "id": "2",
      "category": "Niche Domination",
      "hashtags": ["#...", "#..."],
      "estimatedReach": "50K-200K",
      "engagementScore": 92
    },
    {
      "id": "3",
      "category": "Broad Appeal",
      "hashtags": ["#...", "#..."],
      "estimatedReach": "1M-5M",
      "engagementScore": 78
    },
    {
      "id": "4",
      "category": "Community Building",
      "hashtags": ["#...", "#..."],
      "estimatedReach": "100K-500K",
      "engagementScore": 88
    }
  ]
}`;
};

const generateThumbnailsPrompt = (params: GenerateThumbnailsParams): string => {
  const { transcript, selectedDescription, selectedHashtags, context } = params;
  
  return `You are an expert thumbnail designer for short-form video platforms.

Create 5 AI image generation prompts for thumbnails based on:

DESCRIPTION:
"""${selectedDescription}"""

HASHTAGS:
${selectedHashtags.join(' ')}

TRANSCRIPT CONTEXT:
"""${transcript.substring(0, 500)}..."""

CONTENT TONE: ${context.tone}
CONTENT TYPE: ${context.contentType}

Create 5 thumbnail prompts with different strategies:

1. FACE-DRIVEN - Expressive facial reaction (shock, curiosity, excitement)
2. TEXT-OVERLAY - Bold text with striking visual background
3. ACTION SHOT - Dynamic moment frozen in time
4. MYSTERY/INTRIGUE - Visual puzzle that demands click
5. TRANSFORMATION - Before/after or contrast visual

Each prompt should:
- Be detailed for AI image generation (Midjourney/DALL-E style)
- Specify lighting, colors, composition
- Explain WHY this thumbnail works psychologically
- Be optimized for mobile viewing (small screen)

Respond in JSON format:
{
  "thumbnailPrompts": [
    {
      "id": "1",
      "style": "Face-Driven",
      "prompt": "Detailed AI image generation prompt...",
      "whyItWorks": "Psychological explanation..."
    },
    {
      "id": "2",
      "style": "Text-Overlay",
      "prompt": "Detailed AI image generation prompt...",
      "whyItWorks": "Psychological explanation..."
    },
    {
      "id": "3",
      "style": "Action Shot",
      "prompt": "Detailed AI image generation prompt...",
      "whyItWorks": "Psychological explanation..."
    },
    {
      "id": "4",
      "style": "Mystery/Intrigue",
      "prompt": "Detailed AI image generation prompt...",
      "whyItWorks": "Psychological explanation..."
    },
    {
      "id": "5",
      "style": "Transformation",
      "prompt": "Detailed AI image generation prompt...",
      "whyItWorks": "Psychological explanation..."
    }
  ]
}`;
};

export const generateDescriptions = async (
  params: GenerateDescriptionsParams
): Promise<DescriptionAngle[]> => {
  const content = await callGroqAPI(
    [
      {
        role: 'system',
        content: 'You are a viral content optimization expert. Always respond with valid JSON.',
      },
      {
        role: 'user',
        content: generateDescriptionsPrompt(params),
      },
    ],
    0.8,
    1500
  );

  if (!content) {
    throw new Error('Failed to generate descriptions');
  }

  const parsed = JSON.parse(content);
  return parsed.descriptions;
};

export const generateHashtags = async (
  params: GenerateHashtagsParams
): Promise<HashtagSet[]> => {
  const content = await callGroqAPI(
    [
      {
        role: 'system',
        content: 'You are a hashtag optimization expert. Always respond with valid JSON.',
      },
      {
        role: 'user',
        content: generateHashtagsPrompt(params),
      },
    ],
    0.7,
    1500
  );

  if (!content) {
    throw new Error('Failed to generate hashtags');
  }

  const parsed = JSON.parse(content);
  return parsed.hashtagSets;
};

export const generateThumbnails = async (
  params: GenerateThumbnailsParams
): Promise<ThumbnailPrompt[]> => {
  const content = await callGroqAPI(
    [
      {
        role: 'system',
        content: 'You are a thumbnail design expert. Always respond with valid JSON.',
      },
      {
        role: 'user',
        content: generateThumbnailsPrompt(params),
      },
    ],
    0.9,
    2000
  );

  if (!content) {
    throw new Error('Failed to generate thumbnail prompts');
  }

  const parsed = JSON.parse(content);
  return parsed.thumbnailPrompts;
};

// Helper to estimate viral score based on TikTok algorithm
export const calculateViralScore = (
  description: string,
  hashtags: string[]
): number => {
  // Simplified algorithm score estimation
  let score = 50;
  
  // Description factors
  if (description.length >= 100 && description.length <= 300) score += 10;
  if (description.includes('?') || description.includes('!')) score += 5;
  if (/\d+/.test(description)) score += 5;
  
  // Hashtag factors
  if (hashtags.length >= 5 && hashtags.length <= 10) score += 10;
  if (hashtags.some(h => h.includes('trending') || h.includes('viral'))) score += 5;
  
  // Engagement words
  const powerWords = ['secret', 'truth', 'revealed', 'never', 'always', 'must', 'need', 'want'];
  if (powerWords.some(word => description.toLowerCase().includes(word))) score += 10;
  
  return Math.min(100, score);
};
