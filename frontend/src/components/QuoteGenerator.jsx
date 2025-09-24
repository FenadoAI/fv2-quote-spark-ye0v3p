import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Separator } from './ui/separator';
import { Quote, Copy, Share2, Sparkles, Heart, Brain, Target, Sun, Star, Lightbulb } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API = `${API_BASE}/api`;

const PREDEFINED_THEMES = [
  { value: 'motivation', label: 'Motivation', icon: Target },
  { value: 'success', label: 'Success', icon: Star },
  { value: 'wisdom', label: 'Wisdom', icon: Brain },
  { value: 'love', label: 'Love', icon: Heart },
  { value: 'inspiration', label: 'Inspiration', icon: Lightbulb },
  { value: 'happiness', label: 'Happiness', icon: Sun },
  { value: 'leadership', label: 'Leadership', icon: Target },
  { value: 'perseverance', label: 'Perseverance', icon: Sparkles }
];

const QuoteGenerator = () => {
  const [selectedTheme, setSelectedTheme] = useState('');
  const [customTheme, setCustomTheme] = useState('');
  const [quote, setQuote] = useState('');
  const [author, setAuthor] = useState('');
  const [theme, setTheme] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const generateQuote = async () => {
    if (!selectedTheme && !customTheme.trim()) {
      toast.error('Please select a theme or enter a custom one');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/generate-quote`, {
        theme: selectedTheme,
        custom_theme: customTheme.trim() || null
      });

      if (response.data.success) {
        setQuote(response.data.quote);
        setAuthor(response.data.author);
        setTheme(response.data.theme);
        toast.success('Quote generated successfully!');
      } else {
        setError(response.data.error || 'Failed to generate quote');
        toast.error('Failed to generate quote');
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message || 'An error occurred';
      setError(errorMsg);
      toast.error('Error generating quote');
      console.error('Quote generation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async () => {
    if (!quote || !author) return;

    const textToCopy = `"${quote}" - ${author}`;

    try {
      await navigator.clipboard.writeText(textToCopy);
      toast.success('Quote copied to clipboard!');
    } catch (err) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = textToCopy;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      toast.success('Quote copied to clipboard!');
    }
  };

  const shareQuote = () => {
    if (!quote || !author) return;

    const shareText = `"${quote}" - ${author}`;
    const shareUrl = window.location.href;

    if (navigator.share) {
      navigator.share({
        title: 'Inspirational Quote',
        text: shareText,
        url: shareUrl
      }).catch((err) => console.log('Error sharing:', err));
    } else {
      // Fallback: copy to clipboard and show social media options
      copyToClipboard();

      // Open Twitter share dialog
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
      window.open(twitterUrl, '_blank', 'width=550,height=420');
    }
  };

  const handleThemeSelect = (value) => {
    setSelectedTheme(value);
    if (value) {
      setCustomTheme('');
    }
  };

  const handleCustomThemeChange = (e) => {
    setCustomTheme(e.target.value);
    if (e.target.value.trim()) {
      setSelectedTheme('');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-4">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4 pt-8">
          <div className="flex justify-center">
            <Quote className="h-12 w-12 text-purple-600" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Quote Generator
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Discover wisdom from famous personalities. Choose a theme or create your own to generate inspiring quotes.
          </p>
        </div>

        {/* Theme Selection */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              Choose Your Theme
            </CardTitle>
            <CardDescription>
              Select from popular themes or enter your own custom theme
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Predefined Themes */}
            <div className="space-y-2">
              <Label htmlFor="theme-select">Popular Themes</Label>
              <Select value={selectedTheme} onValueChange={handleThemeSelect}>
                <SelectTrigger id="theme-select" className="h-12">
                  <SelectValue placeholder="Select a theme..." />
                </SelectTrigger>
                <SelectContent>
                  {PREDEFINED_THEMES.map((theme) => {
                    const IconComponent = theme.icon;
                    return (
                      <SelectItem key={theme.value} value={theme.value}>
                        <div className="flex items-center gap-2">
                          <IconComponent className="h-4 w-4" />
                          {theme.label}
                        </div>
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-4">
              <Separator className="flex-1" />
              <span className="text-sm text-gray-500 font-medium">OR</span>
              <Separator className="flex-1" />
            </div>

            {/* Custom Theme */}
            <div className="space-y-2">
              <Label htmlFor="custom-theme">Custom Theme</Label>
              <Input
                id="custom-theme"
                type="text"
                placeholder="Enter your own theme (e.g., creativity, friendship, adventure)"
                value={customTheme}
                onChange={handleCustomThemeChange}
                className="h-12"
              />
            </div>

            {/* Generate Button */}
            <Button
              onClick={generateQuote}
              disabled={isLoading || (!selectedTheme && !customTheme.trim())}
              className="w-full h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Generating...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Generate Quote
                </div>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Quote Display */}
        {(quote || error) && (
          <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
            <CardContent className="p-8">
              {error ? (
                <div className="text-center text-red-600 py-4">
                  <p className="font-medium">Oops! Something went wrong</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              ) : (
                <div className="text-center space-y-6">
                  {/* Theme Badge */}
                  <div className="flex justify-center">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 capitalize">
                      {theme}
                    </span>
                  </div>

                  {/* Quote */}
                  <blockquote className="text-2xl md:text-3xl font-serif text-gray-800 leading-relaxed max-w-3xl mx-auto">
                    "{quote}"
                  </blockquote>

                  {/* Author */}
                  <div className="flex justify-center">
                    <cite className="text-lg font-medium text-gray-600 not-italic">
                      — {author}
                    </cite>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col sm:flex-row gap-3 justify-center items-center pt-4">
                    <Button
                      onClick={copyToClipboard}
                      variant="outline"
                      className="flex items-center gap-2 h-11 px-6"
                    >
                      <Copy className="h-4 w-4" />
                      Copy to Clipboard
                    </Button>
                    <Button
                      onClick={shareQuote}
                      className="flex items-center gap-2 h-11 px-6 bg-blue-600 hover:bg-blue-700"
                    >
                      <Share2 className="h-4 w-4" />
                      Share Quote
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm pb-8">
          <p>Powered by AI • Quotes from famous personalities throughout history</p>
        </div>
      </div>
    </div>
  );
};

export default QuoteGenerator;