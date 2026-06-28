import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Box, Cylinder, Grid, Environment, Html, ContactShadows } from '@react-three/drei';

function HelicopterModel({ pitch, yaw, targetPitch, targetYaw }) {
  const yawRef = useRef();
  const pitchRef = useRef();
  
  // Propeller refs for animation
  const prop1Ref = useRef();
  const prop2Ref = useRef();

  useFrame(() => {
    // Directly assign physical states from HIL backend (no smoothing) to show true overshoot and oscillation
    if (yawRef.current) {
      yawRef.current.rotation.y = yaw;
    }
    if (pitchRef.current) {
      // Invert pitch so positive = nose up
      pitchRef.current.rotation.x = -pitch;
    }
    
    // Spin propellers fast
    if (prop1Ref.current) prop1Ref.current.rotation.y += 0.4;
    if (prop2Ref.current) prop2Ref.current.rotation.y += 0.5;
  });

  return (
    <group>
      {/* Base Pillar */}
      <Cylinder args={[0.3, 0.6, 3, 32]} position={[0, 1.5, 0]}>
        <meshStandardMaterial color="#1e293b" metalness={0.5} roughness={0.2} />
      </Cylinder>
      
      {/* Yaw Joint */}
      <group position={[0, 3, 0]} ref={yawRef}>
        <Cylinder args={[0.2, 0.2, 0.6, 32]} rotation={[Math.PI/2, 0, 0]}>
          <meshStandardMaterial color="#475569" />
        </Cylinder>
        
        {/* Pitch Joint & Helicopter Body */}
        <group ref={pitchRef}>
          {/* HUD Overlay */}
          <Html position={[0, 1.5, 0]} center style={{pointerEvents: 'none', zIndex: 10}}>
            <div style={{background: 'rgba(0,0,0,0.6)', padding: '8px 12px', borderRadius: 8, color: 'white', whiteSpace: 'nowrap', border: '1px solid #444', borderLeft: '4px solid #3b82f6'}}>
              <div style={{fontSize: 11, color: '#aaa', borderBottom: '1px solid #444', paddingBottom: 4, marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1}}>Live Telemetry</div>
              <div style={{display: 'flex', gap: 16}}>
                 <div><span style={{color: '#60a5fa'}}>Pitch:</span> {(pitch*180/Math.PI).toFixed(1)}° <span style={{color:'#666', fontSize: 11}}>tgt: {(targetPitch*180/Math.PI).toFixed(1)}°</span></div>
                 <div><span style={{color: '#f59e0b'}}>Yaw:</span> {(yaw*180/Math.PI).toFixed(1)}° <span style={{color:'#666', fontSize: 11}}>tgt: {(targetYaw*180/Math.PI).toFixed(1)}°</span></div>
              </div>
            </div>
          </Html>

          {/* Pivot Connector */}
          <Box args={[0.15, 1.0, 0.15]} position={[0, 0.5, 0]}>
            <meshStandardMaterial color="#94a3b8" />
          </Box>

          <group position={[0, 1.0, 0]}>
            {/* Cabin (Main Body) */}
            <Box args={[0.8, 1.0, 2.0]} position={[0, 0, 1.0]}>
              <meshStandardMaterial color="#3b82f6" roughness={0.3} metalness={0.4} />
            </Box>
            
            {/* Cockpit Window */}
            <Box args={[0.7, 0.4, 0.8]} position={[0, 0.3, 1.65]}>
              <meshStandardMaterial color="#111" roughness={0.1} metalness={0.9} />
            </Box>

            {/* Landing Skids */}
            <group position={[0, -0.6, 1.0]}>
              <Cylinder args={[0.04, 0.04, 2.2, 8]} position={[0.4, 0, 0]} rotation={[Math.PI/2, 0, 0]}>
                <meshStandardMaterial color="#aaa" />
              </Cylinder>
              <Cylinder args={[0.04, 0.04, 2.2, 8]} position={[-0.4, 0, 0]} rotation={[Math.PI/2, 0, 0]}>
                <meshStandardMaterial color="#aaa" />
              </Cylinder>
              {/* Struts */}
              <Cylinder args={[0.02, 0.02, 0.5, 8]} position={[0.4, 0.25, 0.5]} rotation={[0, 0, -0.2]}>
                <meshStandardMaterial color="#aaa" />
              </Cylinder>
              <Cylinder args={[0.02, 0.02, 0.5, 8]} position={[-0.4, 0.25, 0.5]} rotation={[0, 0, 0.2]}>
                <meshStandardMaterial color="#aaa" />
              </Cylinder>
              <Cylinder args={[0.02, 0.02, 0.5, 8]} position={[0.4, 0.25, -0.5]} rotation={[0, 0, -0.2]}>
                <meshStandardMaterial color="#aaa" />
              </Cylinder>
              <Cylinder args={[0.02, 0.02, 0.5, 8]} position={[-0.4, 0.25, -0.5]} rotation={[0, 0, 0.2]}>
                <meshStandardMaterial color="#aaa" />
              </Cylinder>
            </group>

            {/* Tail Boom */}
            <Cylinder args={[0.15, 0.1, 3.5, 16]} position={[0, 0, -1.75]} rotation={[Math.PI/2, 0, 0]}>
              <meshStandardMaterial color="#1e293b" />
            </Cylinder>

            {/* Tail Fin */}
            <Box args={[0.05, 0.8, 0.4]} position={[0, 0.3, -3.3]}>
              <meshStandardMaterial color="#3b82f6" />
            </Box>

            {/* Main Rotor Assembly */}
            <group position={[0, 0.5, 1.0]}>
              {/* Mast */}
              <Cylinder args={[0.05, 0.08, 0.4, 16]} position={[0, 0.2, 0]}>
                <meshStandardMaterial color="#cbd5e1" />
              </Cylinder>
              {/* Propeller */}
              <group ref={prop1Ref} position={[0, 0.4, 0]}>
                <Box args={[0.1, 0.02, 3.5]}>
                  <meshStandardMaterial color="#111" />
                </Box>
                <Cylinder args={[1.75, 1.75, 0.01, 32]}>
                  <meshStandardMaterial color="#ffffff" transparent opacity={0.15} />
                </Cylinder>
              </group>
            </group>

            {/* Tail Rotor Assembly */}
            <group position={[0.05, 0.6, -3.3]} rotation={[0, 0, -Math.PI/2]}>
              {/* Mast */}
              <Cylinder args={[0.03, 0.03, 0.2, 16]} position={[0, 0.1, 0]}>
                <meshStandardMaterial color="#cbd5e1" />
              </Cylinder>
              {/* Propeller */}
              <group ref={prop2Ref} position={[0, 0.2, 0]}>
                <Box args={[0.05, 0.02, 0.8]}>
                  <meshStandardMaterial color="#111" />
                </Box>
                <Cylinder args={[0.4, 0.4, 0.01, 16]}>
                  <meshStandardMaterial color="#ffffff" transparent opacity={0.15} />
                </Cylinder>
              </group>
            </group>
          </group>

        </group>
      </group>
    </group>
  );
}

export default function Helicopter3D({ pitch, yaw, targetPitch, targetYaw }) {
  return (
    <Canvas camera={{ position: [5, 6, 8], fov: 50 }}>
      {/* PBR Environment for realistic reflections */}
      <Environment preset="city" />
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1.5} castShadow />
      
      <HelicopterModel pitch={pitch} yaw={yaw} targetPitch={targetPitch} targetYaw={targetYaw} />
      
      {/* Floor Grid */}
      <Grid infiniteGrid fadeDistance={40} sectionColor="#444" cellColor="#222" cellThickness={1.0} sectionThickness={2.0} />
      
      {/* Soft Contact Shadows on the floor */}
      <ContactShadows position={[0, 0, 0]} opacity={0.6} scale={15} blur={2.5} far={4} />

      <OrbitControls enablePan={false} maxPolarAngle={Math.PI / 2 + 0.1} />
    </Canvas>
  );
}
