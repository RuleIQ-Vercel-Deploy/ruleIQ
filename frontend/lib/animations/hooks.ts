import { useInView } from 'react-intersection-observer';
import { useAnimation, AnimationControls } from 'framer-motion';
import { useEffect } from 'react';

/**
 * Custom hooks for animations
 */

// Hook for scroll-triggered animations
export function useScrollAnimation(threshold = 0.1) {
  const controls = useAnimation();
  const [ref, inView] = useInView({
    threshold,
    triggerOnce: true,
  });

  useEffect(() => {
    if (inView) {
      controls.start('visible');
    }
  }, [controls, inView]);

  return {
    ref,
    controls,
    initial: 'hidden',
    animate: controls,
  };
}

// Hook for staggered animations
export function useStaggerAnimation(
  inView: boolean,
  staggerChildren = 0.1,
  delayChildren = 0
) {
  const controls = useAnimation();

  useEffect(() => {
    if (inView) {
      controls.start({
        transition: {
          staggerChildren,
          delayChildren,
        },
      });
    }
  }, [controls, inView, staggerChildren, delayChildren]);

  return controls;
}

// Hook for parallax scrolling effect
export function useParallax(offset = 50) {
  const [ref, inView] = useInView({
    threshold: 0,
  });

  return {
    ref,
    style: {
      transform: inView ? 'translateY(0px)' : `translateY(${offset}px)`,
      transition: 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
    },
  };
}

// Hook for reduced motion preference
export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
}

// Hook for gesture-based animations
export function useGestureAnimation() {
  const controls = useAnimation();

  const handleDragEnd = async (_: any, info: any) => {
    const offset = info.offset.x;
    const velocity = info.velocity.x;

    if (Math.abs(velocity) >= 500 || Math.abs(offset) >= 100) {
      await controls.start({
        x: offset > 0 ? 200 : -200,
        opacity: 0,
        transition: { duration: 0.2 },
      });
    } else {
      controls.start({
        x: 0,
        opacity: 1,
        transition: { type: 'spring', stiffness: 300, damping: 30 },
      });
    }
  };

  return {
    controls,
    dragConstraints: { left: 0, right: 0 },
    dragElastic: 1,
    onDragEnd: handleDragEnd,
  };
}

// Hook for auto-animating numbers
export function useCountAnimation(
  end: number,
  duration = 2,
  start = 0
) {
  const [count, setCount] = useState(start);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      
      setCount(Math.floor(progress * (end - start) + start));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration, start]);

  return count;
}

// Add missing import
import { useState } from 'react';