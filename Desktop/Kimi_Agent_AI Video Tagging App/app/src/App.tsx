import { useState } from 'react';
import { 
  Sparkles, 
  Hash, 
  Image, 
  Copy, 
  Check, 
  RefreshCw, 
  TrendingUp, 
  Target, 
  Zap,
  ChevronRight,
  ChevronLeft,
  Settings,
  Info,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import type { Platform, ContextQuestions, DescriptionAngle, HashtagSet, ThumbnailPrompt } from '@/types';
import { PLATFORM_CONFIGS } from '@/types';
import { 
  generateDescriptions, 
  generateHashtags, 
  generateThumbnails
} from '@/services/groqService';
import './App.css';

type Step = 'input' | 'descriptions' | 'hashtags' | 'thumbnails' | 'results';

function App() {
  // Input states
  const [transcript, setTranscript] = useState('');
  const [platform, setPlatform] = useState<Platform>('tiktok');
  const [context, setContext] = useState<ContextQuestions>({
    tone: 'comedy',
    contentType: 'entertainment',
  });
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);

  // Generated content states
  const [descriptions, setDescriptions] = useState<DescriptionAngle[]>([]);
  const [selectedDescription, setSelectedDescription] = useState<DescriptionAngle | null>(null);
  const [hashtagSets, setHashtagSets] = useState<HashtagSet[]>([]);
  const [customHashtags, setCustomHashtags] = useState<string>('');
  const [thumbnailPrompts, setThumbnailPrompts] = useState<ThumbnailPrompt[]>([]);

  // UI states
  const [currentStep, setCurrentStep] = useState<Step>('input');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const platformConfig = PLATFORM_CONFIGS[platform];

  const handleGenerateDescriptions = async () => {
    if (!transcript.trim()) {
      setError('Please enter a transcript');
      return;
    }
    if (!apiKey.trim()) {
      setError('Please enter your Groq API key');
      setShowApiKey(true);
      return;
    }

    setLoading(true);
    setError(null);

    // Set API key in env
    (import.meta.env as Record<string, string>).VITE_GROQ_API_KEY = apiKey;

    try {
      const generatedDescriptions = await generateDescriptions({
        transcript,
        context,
        platform,
      });
      setDescriptions(generatedDescriptions);
      setCurrentStep('descriptions');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate descriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDescription = async (description: DescriptionAngle) => {
    setSelectedDescription(description);
    setLoading(true);
    setError(null);

    try {
      const generatedHashtags = await generateHashtags({
        transcript,
        selectedDescription: description.description,
        context,
        platform,
      });
      setHashtagSets(generatedHashtags);
      setCurrentStep('hashtags');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate hashtags');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHashtags = async (hashtagSet: HashtagSet) => {
    setCustomHashtags(hashtagSet.hashtags.join(' '));
    setLoading(true);
    setError(null);

    try {
      const generatedThumbnails = await generateThumbnails({
        transcript,
        selectedDescription: selectedDescription!.description,
        selectedHashtags: hashtagSet.hashtags,
        context,
      });
      setThumbnailPrompts(generatedThumbnails);
      setCurrentStep('thumbnails');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate thumbnails');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const getViralScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-orange-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 via-purple-500 to-cyan-500 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                ViralContent AI
              </h1>
              <p className="text-xs text-slate-400">Optimize for TikTok & Fanworlds</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Dialog open={showApiKey} onOpenChange={setShowApiKey}>
              <DialogTrigger asChild>
                <Button variant="ghost" size="sm" className="text-slate-400 hover:text-white">
                  <Settings className="w-4 h-4 mr-2" />
                  API Key
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-slate-900 border-slate-700">
                <DialogHeader>
                  <DialogTitle>Configure Groq API Key</DialogTitle>
                  <DialogDescription className="text-slate-400">
                    Enter your Groq API key to use the AI features. Your key is stored locally.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <div>
                    <Label htmlFor="api-key">API Key</Label>
                    <Input
                      id="api-key"
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="gsk_..."
                      className="bg-slate-800 border-slate-700 mt-2"
                    />
                  </div>
                  <p className="text-xs text-slate-500">
                    Get your API key from{' '}
                    <a 
                      href="https://console.groq.com" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-purple-400 hover:underline"
                    >
                      console.groq.com
                    </a>
                  </p>
                </div>
              </DialogContent>
            </Dialog>

            <Select value={platform} onValueChange={(v) => setPlatform(v as Platform)}>
              <SelectTrigger className="w-40 bg-slate-800 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="tiktok">
                  <div className="flex items-center gap-2">
                    <span>TikTok</span>
                  </div>
                </SelectItem>
                <SelectItem value="fanworlds">Fanworlds</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="border-b border-slate-800 bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-center gap-2">
            {[
              { id: 'input', label: 'Input', icon: Sparkles },
              { id: 'descriptions', label: 'Descriptions', icon: Target },
              { id: 'hashtags', label: 'Hashtags', icon: Hash },
              { id: 'thumbnails', label: 'Thumbnails', icon: Image },
            ].map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.id;
              const isCompleted = 
                (step.id === 'input' && currentStep !== 'input') ||
                (step.id === 'descriptions' && ['hashtags', 'thumbnails', 'results'].includes(currentStep)) ||
                (step.id === 'hashtags' && ['thumbnails', 'results'].includes(currentStep)) ||
                (step.id === 'thumbnails' && currentStep === 'results');
              
              return (
                <div key={step.id} className="flex items-center">
                  <div 
                    className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                      isActive 
                        ? 'bg-gradient-to-r from-pink-500/20 to-purple-500/20 border border-pink-500/50' 
                        : isCompleted
                        ? 'bg-green-500/10 border border-green-500/30'
                        : 'bg-slate-800/50 text-slate-500'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${
                      isActive ? 'text-pink-400' : isCompleted ? 'text-green-400' : 'text-slate-500'
                    }`} />
                    <span className={`text-sm font-medium ${
                      isActive ? 'text-white' : isCompleted ? 'text-green-400' : 'text-slate-500'
                    }`}>
                      {step.label}
                    </span>
                  </div>
                  {index < 3 && (
                    <ChevronRight className="w-4 h-4 text-slate-600 mx-2" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert className="mb-6 bg-red-500/10 border-red-500/30">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <AlertDescription className="text-red-400">{error}</AlertDescription>
          </Alert>
        )}

        {/* Step 1: Input */}
        {currentStep === 'input' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-2xl">Paste Your Video Transcript</CardTitle>
                <CardDescription className="text-slate-400">
                  Our AI will analyze the content and generate optimized descriptions, hashtags, and thumbnail ideas.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label htmlFor="transcript" className="text-slate-300">
                    Transcript
                  </Label>
                  <Textarea
                    id="transcript"
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Paste your video transcript here..."
                    className="mt-2 min-h-[200px] bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 resize-none"
                  />
                  <p className="text-xs text-slate-500 mt-2">
                    {transcript.length} characters
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-slate-300">Content Tone</Label>
                    <Select 
                      value={context.tone} 
                      onValueChange={(v) => setContext({ ...context, tone: v as ContextQuestions['tone'] })}
                    >
                      <SelectTrigger className="mt-2 bg-slate-800 border-slate-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="serious">Serious</SelectItem>
                        <SelectItem value="comedy">Comedy</SelectItem>
                        <SelectItem value="deadpan">Deadpan</SelectItem>
                        <SelectItem value="educational">Educational</SelectItem>
                        <SelectItem value="inspirational">Inspirational</SelectItem>
                        <SelectItem value="controversial">Controversial</SelectItem>
                        <SelectItem value="sarcastic">Sarcastic</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label className="text-slate-300">Content Type</Label>
                    <Select 
                      value={context.contentType} 
                      onValueChange={(v) => setContext({ ...context, contentType: v as ContextQuestions['contentType'] })}
                    >
                      <SelectTrigger className="mt-2 bg-slate-800 border-slate-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="storytelling">Storytelling</SelectItem>
                        <SelectItem value="tutorial">Tutorial</SelectItem>
                        <SelectItem value="reaction">Reaction</SelectItem>
                        <SelectItem value="commentary">Commentary</SelectItem>
                        <SelectItem value="entertainment">Entertainment</SelectItem>
                        <SelectItem value="news">News</SelectItem>
                        <SelectItem value="lifestyle">Lifestyle</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-4 bg-slate-800/50 rounded-lg">
                  <Info className="w-4 h-4 text-slate-400" />
                  <p className="text-sm text-slate-400">
                    Optimizing for <span className="text-white font-medium">{platformConfig.name}</span> • 
                    Max {platformConfig.maxHashtags} hashtags • 
                    {platformConfig.characterLimit} character limit
                  </p>
                </div>

                <Button
                  onClick={handleGenerateDescriptions}
                  disabled={loading || !transcript.trim()}
                  className="w-full bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 hover:opacity-90 text-white font-semibold py-6"
                >
                  {loading ? (
                    <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                  ) : (
                    <Sparkles className="w-5 h-5 mr-2" />
                  )}
                  {loading ? 'Analyzing Content...' : 'Generate Descriptions'}
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 2: Descriptions */}
        {currentStep === 'descriptions' && descriptions.length > 0 && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Choose Your Angle</h2>
              <p className="text-slate-400">Select the description that best fits your content strategy</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {descriptions.map((desc, index) => {
                const colors = [
                  'from-pink-500 to-rose-500',
                  'from-purple-500 to-violet-500',
                  'from-cyan-500 to-blue-500',
                ];
                
                return (
                  <Card 
                    key={desc.id} 
                    className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all cursor-pointer group"
                    onClick={() => handleSelectDescription(desc)}
                  >
                    <CardHeader>
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors[index]} flex items-center justify-center mb-4`}>
                        {index === 0 && <Target className="w-6 h-6 text-white" />}
                        {index === 1 && <Zap className="w-6 h-6 text-white" />}
                        {index === 2 && <TrendingUp className="w-6 h-6 text-white" />}
                      </div>
                      <CardTitle className="text-lg">{desc.angle}</CardTitle>
                      <CardDescription className="text-slate-400 text-sm">
                        {desc.reasoning}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="p-4 bg-slate-800/50 rounded-lg">
                        <p className="text-white whitespace-pre-wrap">{desc.description}</p>
                      </div>
                      <Button 
                        className="w-full mt-4 bg-slate-800 hover:bg-slate-700 group-hover:bg-gradient-to-r group-hover:from-pink-500 group-hover:to-purple-500 transition-all"
                      >
                        Select This Angle
                        <ChevronRight className="w-4 h-4 ml-2" />
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="flex justify-center">
              <Button 
                variant="ghost" 
                onClick={() => setCurrentStep('input')}
                className="text-slate-400"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Back to Input
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Hashtags */}
        {currentStep === 'hashtags' && hashtagSets.length > 0 && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Select Hashtag Strategy</h2>
              <p className="text-slate-400">Choose the hashtag set that aligns with your reach goals</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {hashtagSets.map((set) => (
                <Card 
                  key={set.id} 
                  className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all"
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{set.category}</CardTitle>
                      <Badge 
                        variant="secondary" 
                        className={`${getViralScoreColor(set.engagementScore)} bg-slate-800`}
                      >
                        Score: {set.engagementScore}
                      </Badge>
                    </div>
                    <CardDescription className="text-slate-400">
                      Est. Reach: {set.estimatedReach}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {set.hashtags.map((tag, i) => (
                        <span 
                          key={i} 
                          className="px-2 py-1 bg-slate-800 rounded text-sm text-slate-300"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <Progress 
                      value={set.engagementScore} 
                      className="h-2 mb-4 bg-slate-800"
                    />
                    <Button 
                      onClick={() => handleSelectHashtags(set)}
                      className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:opacity-90"
                    >
                      Select & Continue
                      <ChevronRight className="w-4 h-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="flex justify-center">
              <Button 
                variant="ghost" 
                onClick={() => setCurrentStep('descriptions')}
                className="text-slate-400"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Back to Descriptions
              </Button>
            </div>
          </div>
        )}

        {/* Step 4: Thumbnails */}
        {currentStep === 'thumbnails' && thumbnailPrompts.length > 0 && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Thumbnail Concepts</h2>
              <p className="text-slate-400">5 AI-generated thumbnail prompts optimized for clicks</p>
            </div>

            {/* Selected Content Summary */}
            <Card className="bg-slate-900/50 border-slate-800 mb-8">
              <CardHeader>
                <CardTitle className="text-lg">Your Optimized Content</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-slate-400 text-sm">Description</Label>
                  <p className="text-white mt-1">{selectedDescription?.description}</p>
                </div>
                <div>
                  <Label className="text-slate-400 text-sm">Hashtags</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {customHashtags.split(' ').map((tag, i) => (
                      <Badge key={i} variant="secondary" className="bg-slate-800">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopy(selectedDescription?.description || '', 'desc')}
                    className="border-slate-700"
                  >
                    {copied === 'desc' ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                    Copy Description
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopy(customHashtags, 'tags')}
                    className="border-slate-700"
                  >
                    {copied === 'tags' ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                    Copy Hashtags
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Thumbnail Prompts */}
            <div className="grid grid-cols-1 gap-6">
              {thumbnailPrompts.map((prompt, index) => {
                const colors = [
                  'border-pink-500/30',
                  'border-purple-500/30',
                  'border-cyan-500/30',
                  'border-blue-500/30',
                  'border-green-500/30',
                ];
                
                return (
                  <Card 
                    key={prompt.id} 
                    className={`bg-slate-900/50 ${colors[index]} hover:border-opacity-60 transition-all`}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-3">
                        <Badge className="bg-slate-800">{prompt.style}</Badge>
                        <CardTitle className="text-base font-medium">Thumbnail {index + 1}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="p-4 bg-slate-800/50 rounded-lg">
                        <p className="text-slate-300 text-sm leading-relaxed">{prompt.prompt}</p>
                      </div>
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-slate-400">{prompt.whyItWorks}</p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopy(prompt.prompt, `thumb-${prompt.id}`)}
                        className="border-slate-700"
                      >
                        {copied === `thumb-${prompt.id}` ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                        Copy Prompt
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="flex justify-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => setCurrentStep('hashtags')}
                className="text-slate-400"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Back to Hashtags
              </Button>
              <Button
                onClick={() => {
                  setTranscript('');
                  setDescriptions([]);
                  setHashtagSets([]);
                  setThumbnailPrompts([]);
                  setSelectedDescription(null);
                  setCurrentStep('input');
                }}
                className="bg-gradient-to-r from-pink-500 to-purple-500"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Start New
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-16 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-500 text-sm">
          <p>Powered by Groq AI • Optimized for viral content</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
