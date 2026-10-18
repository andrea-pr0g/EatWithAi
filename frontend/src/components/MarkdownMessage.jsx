import React, { useMemo } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Configure marked options
marked.setOptions({
  breaks: true, // Render single line breaks as <br>
  gfm: true,    // GitHub flavored markdown
});

export default function MarkdownMessage({ content, isBot = true }) {
  const formattedHtml = useMemo(() => {
    if (!content) return '';
    try {
      // Parse markdown to HTML
      const rawHtml = marked.parse(content);
      // Sanitize HTML with DOMPurify
      return DOMPurify.sanitize(rawHtml);
    } catch (err) {
      // Fallback to text if error
      return content;
    }
  }, [content]);

  return (
    <div 
      className={`chat-markdown ${isBot ? 'text-slate-100' : 'text-white'}`}
      dangerouslySetInnerHTML={{ __html: formattedHtml }} 
    />
  );
}
