export type Platform = 'tiktok' | 'fanworlds' | 'custom';

export interface PlatformConfig {
  name: string;
  maxDescriptionLength: number;
  maxHashtags: number;
  hashtagWeightFormula: 'engagement' | 'viral' | 'balanced';
  characterLimit: number;
}

export interface ContextQuestions {
  tone: 'serious' | 'comedy' | 'deadpan' | 'educational' | 'inspirational' | 'controversial' | 'sarcastic';
  contentType: 'storytelling' | 'tutorial' | 'reaction' | 'commentary' | 'entertainment' | 'news' | 'lifestyle';
}

export interface DescriptionAngle {
  id: string;
  angle: string;
  description: string;
  reasoning: string;
}

export interface HashtagSet {
  id: string;
  category: string;
  hashtags: string[];
  estimatedReach: string;
  engagementScore: number;
}

export interface ThumbnailPrompt {
  id: string;
  prompt: string;
  style: string;
  whyItWorks: string;
}

export interface GeneratedContent {
  descriptions: DescriptionAngle[];
  hashtagSets: HashtagSet[];
  thumbnailPrompts: ThumbnailPrompt[];
}

export interface TikTokAlgorithmWeights {
  completionRate: number;
  shares: number;
  comments: number;
  likes: number;
  watchTime: number;
  rewatches: number;
}

export const PLATFORM_CONFIGS: Record<Platform, PlatformConfig> = {
  tiktok: {
    name: 'TikTok',
    maxDescriptionLength: 2200,
    maxHashtags: 10,
    hashtagWeightFormula: 'viral',
    characterLimit: 2200,
  },
  fanworlds: {
    name: 'Fanworlds',
    maxDescriptionLength: 1500,
    maxHashtags: 15,
    hashtagWeightFormula: 'engagement',
    characterLimit: 1500,
  },
  custom: {
    name: 'Custom Platform',
    maxDescriptionLength: 2000,
    maxHashtags: 12,
    hashtagWeightFormula: 'balanced',
    characterLimit: 2000,
  },
};

export const TIKTOK_ALGORITHM_WEIGHTS: TikTokAlgorithmWeights = {
  completionRate: 0.30,
  shares: 0.25,
  comments: 0.20,
  likes: 0.10,
  watchTime: 0.10,
  rewatches: 0.05,
};

export const HASHTAG_CATEGORIES = [
  { id: 'trending', name: 'Trending', weight: 0.35 },
  { id: 'niche', name: 'Niche Specific', weight: 0.25 },
  { id: 'broad', name: 'Broad Appeal', weight: 0.20 },
  { id: 'community', name: 'Community', weight: 0.20 },
];
