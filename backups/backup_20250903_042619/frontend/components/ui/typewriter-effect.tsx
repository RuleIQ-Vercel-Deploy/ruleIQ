'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

type TypewriterWord = {
  text: string;
  className?: string;
};

type TypewriterEffectProps = {
  words: TypewriterWord[];
  className?: string;
  cursorClassName?: string;
};

export function TypewriterEffect({ words, className, cursorClassName }: TypewriterEffectProps) {
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentWord = words[currentWordIndex]?.text || '';
    const timeout = setTimeout(
      () => {
        if (!isDeleting) {
          if (currentText.length < currentWord.length) {
            setCurrentText(currentWord.substring(0, currentText.length + 1));
          } else {
            setTimeout(() => setIsDeleting(true), 1500);
          }
        } else {
          if (currentText.length > 0) {
            setCurrentText(currentWord.substring(0, currentText.length - 1));
          } else {
            setIsDeleting(false);
            setCurrentWordIndex((prev) => (prev + 1) % words.length);
          }
        }
      },
      isDeleting ? 50 : 100,
    );

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, currentWordIndex, words]);

  const currentWord = words[currentWordIndex];

  return (
    <div className={cn('flex items-center space-x-1', className)}>
      <motion.span
        key={currentWordIndex}
        className={cn('inline-block', currentWord?.className)}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {currentText}
      </motion.span>
      <motion.span
        className={cn('inline-block h-4 w-0.5 bg-current', cursorClassName)}
        animate={{ opacity: [0, 1, 0] }}
        transition={{ duration: 1, repeat: Infinity }}
      />
    </div>
  );
}
