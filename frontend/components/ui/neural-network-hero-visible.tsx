'use client';

import { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame, extend } from '@react-three/fiber';
import { shaderMaterial } from '@react-three/drei';
import * as THREE from 'three';

import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { SplitText } from 'gsap/SplitText';

gsap.registerPlugin(SplitText);

// ===================== SHADER =====================
const vertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

// Simplified, more visible neural network shader
const fragmentShader = `
  uniform float iTime;
  uniform vec2 iResolution;
  varying vec2 vUv;
  
  float noise(vec2 p) {
    return sin(p.x * 10.0) * sin(p.y * 10.0);
  }
  
  void main() {
    vec2 uv = vUv;
    vec2 center = vec2(0.5);
    
    // Create animated neural network pattern
    float t = iTime * 0.5;
    
    // Multiple layers of connections
    vec3 color = vec3(0.0);
    
    for(float i = 0.0; i < 5.0; i++) {
      vec2 pos = uv * 3.0 + vec2(sin(t + i), cos(t + i * 0.7));
      
      // Neural nodes
      float node = 0.0;
      for(float j = 0.0; j < 3.0; j++) {
        vec2 nodePos = vec2(
          sin(j * 2.1 + t * 0.3 + i) * 0.5 + 0.5,
          cos(j * 1.7 + t * 0.2 + i) * 0.5 + 0.5
        );
        float dist = distance(uv, nodePos);
        node += 0.02 / (dist + 0.01);
      }
      
      // Connections between nodes
      float connection = abs(sin(pos.x * 5.0 + t) * sin(pos.y * 5.0 - t * 0.7));
      connection = pow(connection, 2.0) * 0.5;
      
      // Purple gradient
      color.r += node * 0.6 + connection * 0.3;
      color.g += node * 0.3 + connection * 0.2;
      color.b += node * 1.0 + connection * 0.6;
    }
    
    // Add pulsing glow
    float pulse = sin(iTime * 2.0) * 0.3 + 0.7;
    color *= pulse;
    
    // Add silver highlights
    float brightness = (color.r + color.g + color.b) / 3.0;
    if(brightness > 0.5) {
      color = mix(color, vec3(0.8, 0.8, 0.85), 0.2);
    }
    
    // Ensure minimum visibility
    color = max(color, vec3(0.1, 0.05, 0.15));
    
    // Fade edges
    float edgeFade = 1.0 - distance(uv, center) * 0.8;
    color *= edgeFade;
    
    gl_FragColor = vec4(color, 0.8);
  }
`;

const NeuralShaderMaterial = shaderMaterial(
  { iTime: 0, iResolution: new THREE.Vector2(1, 1) },
  vertexShader,
  fragmentShader
);

extend({ NeuralShaderMaterial });

function ShaderPlane() {
  const meshRef = useRef<THREE.Mesh>(null!);
  const materialRef = useRef<any>(null!);

  useFrame((state) => {
    if (!materialRef.current) return;
    materialRef.current.iTime = state.clock.elapsedTime;
    const { width, height } = state.size;
    materialRef.current.iResolution.set(width, height);
  });

  return (
    <mesh ref={meshRef} position={[0, 0, 0]}>
      <planeGeometry args={[6, 6]} />
      <neuralShaderMaterial ref={materialRef} side={THREE.DoubleSide} transparent />
    </mesh>
  );
}

function ShaderBackground() {
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const [isReady, setIsReady] = useState(false);
  
  const camera = useMemo(() => ({ 
    position: [0, 0, 2] as [number, number, number], 
    fov: 75, 
    near: 0.1, 
    far: 10 
  }), []);
  
  useEffect(() => {
    // Delay to ensure single mount
    const timer = setTimeout(() => setIsReady(true), 100);
    return () => clearTimeout(timer);
  }, []);
  
  useGSAP(
    () => {
      if (!canvasRef.current) return;
      
      gsap.set(canvasRef.current, {
        autoAlpha: 0
      });
      
      gsap.to(canvasRef.current, {
        autoAlpha: 1,
        duration: 2,
        ease: 'power2.inOut',
        delay: 0.5
      });
    },
    { scope: canvasRef, dependencies: [isReady] }
  );
  
  if (!isReady) {
    return (
      <div className="absolute inset-0 -z-10 w-full h-full bg-black" aria-hidden />
    );
  }
  
  return (
    <div ref={canvasRef} className="absolute inset-0 -z-10 w-full h-full" aria-hidden>
      <Canvas
        camera={camera}
        gl={{ 
          antialias: false,
          alpha: true, 
          preserveDrawingBuffer: false,
          powerPreference: 'low-power',
          stencil: false,
          depth: false
        }}
        dpr={1}
        style={{ width: '100%', height: '100%', background: 'transparent' }}
      >
        <ShaderPlane />
      </Canvas>
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/60" />
    </div>
  );
}

// ===================== HERO =====================
interface HeroProps {
  title: string;
  description: string;
  badgeText?: string;
  badgeLabel?: string;
  ctaButtons?: Array<{ text: string; href: string; primary?: boolean }>;
  microDetails?: Array<string>;
}

export default function Hero({
  title,
  description,
  badgeText = "Generative Surfaces",
  badgeLabel = "New",
  ctaButtons = [
    { text: "Get started", href: "#get-started", primary: true },
    { text: "View showcase", href: "#showcase" }
  ],
  microDetails = ["Low‑weight font", "Tight tracking", "Subtle motion"]
}: HeroProps) {
  const sectionRef = useRef<HTMLElement | null>(null);
  const headerRef = useRef<HTMLHeadingElement | null>(null);
  const paraRef = useRef<HTMLParagraphElement | null>(null);
  const ctaRef = useRef<HTMLDivElement | null>(null);
  const badgeRef = useRef<HTMLDivElement | null>(null);
  const microRef = useRef<HTMLUListElement | null>(null);
  const microItem1Ref = useRef<HTMLLIElement | null>(null);
  const microItem2Ref = useRef<HTMLLIElement | null>(null);
  const microItem3Ref = useRef<HTMLLIElement | null>(null);

  useGSAP(
    () => {
      if (!headerRef.current) return;

      document.fonts.ready.then(() => {
        const split = SplitText.create(headerRef.current!, {
          type: 'lines',
          linesClass: 'split-line',
        });

        gsap.set(split.lines, {
          filter: 'blur(16px)',
          yPercent: 30,
          autoAlpha: 0,
          scale: 1.06,
          transformOrigin: '50% 100%',
        });

        if (badgeRef.current) {
          gsap.set(badgeRef.current, { autoAlpha: 0, y: -8 });
        }
        if (paraRef.current) {
          gsap.set(paraRef.current, { autoAlpha: 0, y: 8 });
        }
        if (ctaRef.current) {
          gsap.set(ctaRef.current, { autoAlpha: 0, y: 8 });
        }
        const microItems = [microItem1Ref.current, microItem2Ref.current, microItem3Ref.current].filter(Boolean);
        if (microItems.length > 0) {
          gsap.set(microItems, { autoAlpha: 0, y: 6 });
        }

        const tl = gsap.timeline({
          defaults: { ease: 'power3.out' },
        });

        if (badgeRef.current) {
          tl.to(badgeRef.current, { autoAlpha: 1, y: 0, duration: 0.5 }, 0.0);
        }

        tl.to(
          split.lines,
          {
            filter: 'blur(0px)',
            yPercent: 0,
            autoAlpha: 1,
            scale: 1,
            duration: 0.9,
            stagger: 0.15,
          },
          0.1,
        );

        if (paraRef.current) {
          tl.to(paraRef.current, { autoAlpha: 1, y: 0, duration: 0.5 }, '-=0.55');
        }
        if (ctaRef.current) {
          tl.to(ctaRef.current, { autoAlpha: 1, y: 0, duration: 0.5 }, '-=0.35');
        }
        if (microItems.length > 0) {
          tl.to(microItems, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.1 }, '-=0.25');
        }
      });
    },
    { scope: sectionRef },
  );

  return (
    <section ref={sectionRef} className="relative h-screen w-screen overflow-hidden bg-black">
      <ShaderBackground />

      <div className="relative mx-auto flex max-w-7xl flex-col items-start gap-6 px-6 pb-24 pt-36 sm:gap-8 sm:pt-44 md:px-10 lg:px-16">
        <div ref={badgeRef} className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 backdrop-blur-sm">
          <span className="text-[10px] font-light uppercase tracking-[0.08em] text-white/70">{badgeLabel}</span>
          <span className="h-1 w-1 rounded-full bg-white/40" />
          <span className="text-xs font-light tracking-tight text-white/80">{badgeText}</span>
        </div>

        <h1 ref={headerRef} className="max-w-2xl text-left text-5xl font-extralight leading-[1.05] tracking-tight text-white sm:text-6xl md:text-7xl">
          {title}
        </h1>

        <p ref={paraRef} className="max-w-xl text-left text-base font-light leading-relaxed tracking-tight text-white/75 sm:text-lg">
          {description}
        </p>

        <div ref={ctaRef} className="flex flex-wrap items-center gap-3 pt-2">
          {ctaButtons.map((button, index) => (
            <a
              key={index}
              href={button.href}
              className={`rounded-2xl border border-white/10 px-5 py-3 text-sm font-light tracking-tight transition-colors focus:outline-none focus:ring-2 focus:ring-white/30 duration-300 ${
                button.primary
                  ? "bg-white/10 text-white backdrop-blur-sm hover:bg-white/20"
                  : "text-white/80 hover:bg-white/5"
              }`}
            >
              {button.text}
            </a>
          ))}
        </div>

        <ul ref={microRef} className="mt-8 flex flex-wrap gap-6 text-xs font-extralight tracking-tight text-white/60">
          {microDetails.map((detail, index) => {
            const refMap = [microItem1Ref, microItem2Ref, microItem3Ref];
            return (
              <li key={index} ref={refMap[index]} className="flex items-center gap-2">
                <span className="h-1 w-1 rounded-full bg-white/40" /> {detail}
              </li>
            );
          })}
        </ul>
      </div>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/40 to-transparent" />
    </section>
  );
}

declare module '@react-three/fiber' {
  interface ThreeElements {
    neuralShaderMaterial: any;
  }
}
