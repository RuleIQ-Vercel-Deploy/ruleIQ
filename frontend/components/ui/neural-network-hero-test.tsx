'use client';

import { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame, extend } from '@react-three/fiber';
import { shaderMaterial } from '@react-three/drei';
import * as THREE from 'three';

// Dynamic imports for GSAP to avoid SSR issues
let gsap: any;
let SplitText: any;
let useGSAP: any;

if (typeof window !== 'undefined') {
  gsap = require('gsap').gsap;
  SplitText = require('gsap/SplitText').SplitText;
  useGSAP = require('@gsap/react').useGSAP;
  
  if (gsap && SplitText) {
    gsap.registerPlugin(SplitText);
  }
}