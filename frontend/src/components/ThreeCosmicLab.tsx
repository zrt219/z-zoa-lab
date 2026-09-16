import React, { useEffect, useRef, useState, useMemo } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export interface GalaxyItem {
  id: string;
  name: string;
  x: number;
  y: number;
  z: number;
  cz: number;
  v_pec: number;
  is_holdout: boolean;
}

export interface VoxelItem {
  x: number;
  y: number;
  z: number;
  delta_density: number;
  delta_sigma: number;
  delta_vx: number;
  delta_vy: number;
  delta_vz: number;
  delta_v_mag: number;
  pred_density: number;
  pred_sigma: number;
  hybrid_density: number;
  hybrid_sigma: number;
  info_gain_pct: number;
}

export interface DifferentialSummary {
  delta_density: { min: number; max: number; mean: number; rms: number };
  delta_sigma: { min: number; max: number; mean: number; rms: number };
  delta_velocity: { min: number; max: number; mean: number; rms: number };
  prediction_density: { min: number; max: number; mean: number };
  hybrid_density: { min: number; max: number; mean: number };
  mean_uncertainty_reduction_pct: number;
}

export interface DifferentialData {
  status: string;
  run_id: string;
  box_size_mpc: number;
  half_box_mpc: number;
  grid_size: number;
  voxel_count: number;
  downsample_step: number;
  summary: DifferentialSummary;
  voxels: VoxelItem[];
  holdout_authorized: boolean;
  holdout_galaxies: GalaxyItem[];
  strict_readonly_safety: string;
}

export type ReconstructionLayerMode =
  | "SURVEY_BASE"
  | "PREDICTION"
  | "HOLDOUT"
  | "HYBRID"
  | "DIFFERENTIAL";

export interface ThreeCosmicLabProps {
  onNavigateToCalc?: () => void;
  selectedRunId?: string;
  initialMode?: ReconstructionLayerMode;
}

export const ThreeCosmicLab: React.FC<ThreeCosmicLabProps> = ({
  onNavigateToCalc,
  selectedRunId = "VELA-001",
  initialMode = "DIFFERENTIAL",
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  // Active Layer Selection Mode
  const [activeLayerMode, setActiveLayerMode] = useState<ReconstructionLayerMode>(initialMode);

  // Differential Sub-Layer Toggles
  const [showDiffDensity, setShowDiffDensity] = useState(true);
  const [showDiffVelocity, setShowDiffVelocity] = useState(true);
  const [showInfoGainHighlight, setShowInfoGainHighlight] = useState(true);
  const [showRevealedHoldout, setShowRevealedHoldout] = useState(true);

  // Standard Survey Layers Visibility State
  const [showHICloud, setShowHICloud] = useState(true);
  const [showCF4Velocity, setShowCF4Velocity] = useState(true);
  const [showMilkyWayPlane, setShowMilkyWayPlane] = useState(true);
  const [showStreamlines, setShowStreamlines] = useState(true);
  const [showGalaxies, setShowGalaxies] = useState(true);
  const [showGridAxes, setShowGridAxes] = useState(true);
  const [showAnnotations, setShowAnnotations] = useState(true);

  // Slicing State
  const [sliceAxis, setSliceAxis] = useState<"z" | "y" | "x">("z");
  const [sliceDepth, setSliceDepth] = useState<number>(200);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  // Selected Object / Voxel Inspectors
  const [selectedObject, setSelectedObject] = useState<GalaxyItem | null>(null);
  const [selectedVoxel, setSelectedVoxel] = useState<VoxelItem | null>(null);

  // Live Data State
  const [volumeData, setVolumeData] = useState<any | null>(null);
  const [differentialData, setDifferentialData] = useState<DifferentialData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [diffLoading, setDiffLoading] = useState<boolean>(true);

  // References for Three.js objects
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  const hiPointsRef = useRef<THREE.Points | null>(null);
  const velocityGroupRef = useRef<THREE.Group | null>(null);
  const milkyWayPlaneRef = useRef<THREE.Mesh | null>(null);
  const streamlinesGroupRef = useRef<THREE.Group | null>(null);
  const galaxiesGroupRef = useRef<THREE.Group | null>(null);
  const gridGroupRef = useRef<THREE.Group | null>(null);
  const annotationsGroupRef = useRef<THREE.Group | null>(null);

  // Differential & Reconstruction Scene References
  const voxelMeshRef = useRef<THREE.InstancedMesh | null>(null);
  const diffVelocityGroupRef = useRef<THREE.Group | null>(null);
  const holdoutGroupRef = useRef<THREE.Group | null>(null);
  const voxelHighlightRef = useRef<THREE.LineSegments | null>(null);

  // 1. Fetch standard 3D cosmic web volume
  useEffect(() => {
    let isMounted = true;
    const fetchVolume = async () => {
      try {
        const res = await fetch("/reconstruction/3d-volume?box_size=300");
        if (res.ok) {
          const data = await res.json();
          if (isMounted) setVolumeData(data);
        }
      } catch (err) {
        console.warn("Backend 3D volume not available, using offline cosmic web.", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchVolume();
    return () => {
      isMounted = false;
    };
  }, []);

  // 2. Fetch Differential Reconstruction Data for selectedRunId
  useEffect(() => {
    let isMounted = true;
    const fetchDiff = async () => {
      try {
        setDiffLoading(true);
        const res = await fetch(
          `/reconstruction/runs/${selectedRunId}/differential?downsample_step=2`
        );
        if (res.ok) {
          const data: DifferentialData = await res.json();
          if (isMounted) setDifferentialData(data);
        } else {
          console.warn("Differential reconstruction endpoint not available yet.");
        }
      } catch (err) {
        console.warn("Error fetching differential fields:", err);
      } finally {
        if (isMounted) setDiffLoading(false);
      }
    };
    fetchDiff();
    return () => {
      isMounted = false;
    };
  }, [selectedRunId]);

  // Sync initialMode if prop updates
  useEffect(() => {
    if (initialMode) setActiveLayerMode(initialMode);
  }, [initialMode]);

  // Fallback / default data if backend isn't responding yet
  const effectiveData = useMemo(() => {
    if (volumeData) return volumeData;
    const points: any[] = [];
    let seed = 1234567;
    const lcg = () => {
      seed = (seed * 1664525 + 1013904223) % 4294967296;
      return seed / 4294967296;
    };

    for (let i = 0; i < 600; i++) {
      const u = lcg();
      const r = Math.pow(u, 0.5) * 120;
      const theta = lcg() * Math.PI * 2;
      const phi = (lcg() - 0.5) * Math.PI;
      const z = (lcg() - 0.5) * 60;
      points.push({
        x: r * Math.cos(theta) * Math.cos(phi),
        y: r * Math.sin(theta) * Math.cos(phi),
        z: z,
        density: lcg() * 2,
        in_zoa: Math.abs(z) < 12,
      });
    }
    const sampleGalaxies: GalaxyItem[] = [
      { id: "G001", name: "Milky Way (Local Group)", x: 0, y: 0, z: 0, cz: 0, v_pec: 0, is_holdout: false },
      { id: "G002", name: "Centaurus A", x: -2.4, y: 2.9, z: -0.8, cz: 547, v_pec: -285, is_holdout: false },
      { id: "G003", name: "Virgo M87", x: -2.1, y: 15.8, z: -0.5, cz: 1307, v_pec: 120, is_holdout: false },
      { id: "G004", name: "NGC 4889 (Coma Cluster)", x: 0.8, y: 74.5, z: 8.2, cz: 6495, v_pec: -310, is_holdout: false },
      { id: "G005", name: "Norma Cluster (Great Attractor)", x: -32.5, y: 14.1, z: -8.5, cz: 4871, v_pec: 560, is_holdout: false },
      { id: "V001", name: "MeerKAT Vela-HI-01", x: -138.2, y: -78.4, z: -4.2, cz: 18200, v_pec: 490, is_holdout: true },
      { id: "V002", name: "MeerKAT Vela-HI-02", x: -142.1, y: -82.0, z: -5.8, cz: 18550, v_pec: 530, is_holdout: true },
    ];
    return {
      box_size_mpc: 300,
      hi_points: points,
      velocity_vectors: [],
      streamlines: [],
      galaxies: sampleGalaxies,
      attractors: [
        { name: "Great Attractor", x: -35, y: 15, z: -10, color: "#DC2626" },
        { name: "Shapley Supercluster", x: -130, y: 70, z: -25, color: "#7C3AED" },
        { name: "Vela Supercluster", x: -140, y: -80, z: -5, color: "#EA580C" },
      ],
    };
  }, [volumeData]);

  // Initialize Three.js Scene
  useEffect(() => {
    if (!mountRef.current) return;
    const container = mountRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight || 580;

    // 1. Scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    const bgColor = isDarkMode ? 0x0f172a : 0xfcfaf7;
    scene.background = new THREE.Color(bgColor);

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 1, 2000);
    camera.position.set(240, 190, 260);
    cameraRef.current = camera;

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      preserveDrawingBuffer: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.localClippingEnabled = true;
    rendererRef.current = renderer;
    container.replaceChildren(renderer.domElement);

    // 4. Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0, 0);
    controlsRef.current = controls;

    // 5. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.65);
    dirLight.position.set(120, 240, 180);
    scene.add(dirLight);

    // 6. Raycaster for clicking galaxies and voxels
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onPointerDown = (event: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);

      // Check Holdout points
      if (holdoutGroupRef.current) {
        const intersects = raycaster.intersectObjects(holdoutGroupRef.current.children, true);
        if (intersects.length > 0) {
          const hitObj = intersects[0].object;
          if (hitObj.userData && hitObj.userData.galaxy) {
            setSelectedObject(hitObj.userData.galaxy);
            setSelectedVoxel(null);
            return;
          }
        }
      }

      // Check Known Galaxies
      if (galaxiesGroupRef.current) {
        const intersects = raycaster.intersectObjects(galaxiesGroupRef.current.children, true);
        if (intersects.length > 0) {
          const hitObj = intersects[0].object;
          if (hitObj.userData && hitObj.userData.galaxy) {
            setSelectedObject(hitObj.userData.galaxy);
            setSelectedVoxel(null);
            return;
          }
        }
      }

      // Check Voxel Mesh (Clickable Voxel Inspector)
      if (voxelMeshRef.current && differentialData && differentialData.voxels) {
        const intersects = raycaster.intersectObject(voxelMeshRef.current, false);
        if (intersects.length > 0 && intersects[0].instanceId !== undefined) {
          const vox = differentialData.voxels[intersects[0].instanceId];
          if (vox) {
            setSelectedVoxel(vox);
            setSelectedObject(null);
            return;
          }
        }
      }
    };
    renderer.domElement.addEventListener("pointerdown", onPointerDown);

    // 7. Render Loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 580;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      renderer.dispose();
      container.replaceChildren();
    };
  }, [isDarkMode, differentialData]);

  // Build / Update Scene Objects when data, mode, or sliceDepth changes
  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene || !effectiveData) return;

    // Clean up old groups
    if (hiPointsRef.current) scene.remove(hiPointsRef.current);
    if (velocityGroupRef.current) scene.remove(velocityGroupRef.current);
    if (milkyWayPlaneRef.current) scene.remove(milkyWayPlaneRef.current);
    if (streamlinesGroupRef.current) scene.remove(streamlinesGroupRef.current);
    if (galaxiesGroupRef.current) scene.remove(galaxiesGroupRef.current);
    if (gridGroupRef.current) scene.remove(gridGroupRef.current);
    if (annotationsGroupRef.current) scene.remove(annotationsGroupRef.current);
    if (voxelMeshRef.current) scene.remove(voxelMeshRef.current);
    if (diffVelocityGroupRef.current) scene.remove(diffVelocityGroupRef.current);
    if (holdoutGroupRef.current) scene.remove(holdoutGroupRef.current);
    if (voxelHighlightRef.current) scene.remove(voxelHighlightRef.current);

    const halfBox = differentialData?.half_box_mpc || (effectiveData.box_size_mpc ? effectiveData.box_size_mpc / 2 : 150);

    // Synchronized Clipping Plane
    const planeNormal =
      sliceAxis === "z"
        ? new THREE.Vector3(0, 0, -1)
        : sliceAxis === "y"
        ? new THREE.Vector3(0, -1, 0)
        : new THREE.Vector3(-1, 0, 0);
    const clipPlane = new THREE.Plane(planeNormal, sliceDepth);

    // --- A. Grid & Coordinate Bounding Box ---
    const gridGroup = new THREE.Group();
    const boxGeo = new THREE.BoxGeometry(halfBox * 2, halfBox * 2, halfBox * 2);
    const boxEdges = new THREE.EdgesGeometry(boxGeo);
    const boxLineMat = new THREE.LineDashedMaterial({
      color: isDarkMode ? 0x475569 : 0x94a3b8,
      dashSize: 6,
      gapSize: 4,
      linewidth: 1,
    });
    const boxLines = new THREE.LineSegments(boxEdges, boxLineMat);
    boxLines.computeLineDistances();
    gridGroup.add(boxLines);

    const gridHelper = new THREE.GridHelper(
      halfBox * 2,
      12,
      isDarkMode ? 0x334155 : 0xcbd5e1,
      isDarkMode ? 0x1e293b : 0xe2e8f0
    );
    gridHelper.position.y = -halfBox;
    gridGroup.add(gridHelper);

    const axes = new THREE.AxesHelper(halfBox * 0.9);
    gridGroup.add(axes);

    gridGroup.visible = showGridAxes;
    gridGroupRef.current = gridGroup;
    scene.add(gridGroup);

    // --- B. Milky Way Obscuration Plane ---
    const planeGeo = new THREE.CylinderGeometry(halfBox * 0.95, halfBox * 0.95, 14, 48);
    const planeMat = new THREE.MeshStandardMaterial({
      color: isDarkMode ? 0x475569 : 0xa8a29e,
      transparent: true,
      opacity: isDarkMode ? 0.28 : 0.22,
      roughness: 0.9,
      clippingPlanes: [clipPlane],
    });
    const mwPlane = new THREE.Mesh(planeGeo, planeMat);
    mwPlane.position.set(0, 0, 0);
    mwPlane.visible = showMilkyWayPlane;
    milkyWayPlaneRef.current = mwPlane;
    scene.add(mwPlane);

    // --- C. Survey H I Point Cloud ---
    if (effectiveData.hi_points && effectiveData.hi_points.length > 0) {
      const pts = effectiveData.hi_points;
      const positions = new Float32Array(pts.length * 3);
      const colors = new Float32Array(pts.length * 3);

      const colBase = new THREE.Color(isDarkMode ? 0x38bdf8 : 0x2563eb);
      const colZoa = new THREE.Color(isDarkMode ? 0xf59e0b : 0xd97706);

      pts.forEach((p: any, i: number) => {
        positions[i * 3] = p.x;
        positions[i * 3 + 1] = p.y;
        positions[i * 3 + 2] = p.z;

        const c = p.in_zoa ? colZoa : colBase;
        colors[i * 3] = c.r;
        colors[i * 3 + 1] = c.g;
        colors[i * 3 + 2] = c.b;
      });

      const ptGeo = new THREE.BufferGeometry();
      ptGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      ptGeo.setAttribute("color", new THREE.BufferAttribute(colors, 3));

      const ptMat = new THREE.PointsMaterial({
        size: isDarkMode ? 3.5 : 4.0,
        vertexColors: true,
        transparent: true,
        opacity: activeLayerMode === "SURVEY_BASE" ? (isDarkMode ? 0.85 : 0.75) : 0.35,
        clippingPlanes: [clipPlane],
      });

      const hiPoints = new THREE.Points(ptGeo, ptMat);
      hiPoints.visible = showHICloud && (activeLayerMode === "SURVEY_BASE" || activeLayerMode === "HOLDOUT");
      hiPointsRef.current = hiPoints;
      scene.add(hiPoints);
    }

    // --- D. CF4 Velocity Vector Field ---
    const velGroup = new THREE.Group();
    if (effectiveData.velocity_vectors && effectiveData.velocity_vectors.length > 0) {
      effectiveData.velocity_vectors.forEach((v: any) => {
        const dir = new THREE.Vector3(v.vx, v.vy, v.vz).normalize();
        const origin = new THREE.Vector3(v.x, v.y, v.z);
        const length = Math.min(Math.max(v.mag * 0.035, 6), 22);
        const hex = isDarkMode ? 0xf43f5e : 0xe11d48;
        const arrow = new THREE.ArrowHelper(dir, origin, length, hex, 4, 2.5);
        velGroup.add(arrow);
      });
    }
    velGroup.visible = showCF4Velocity && activeLayerMode === "SURVEY_BASE";
    velocityGroupRef.current = velGroup;
    scene.add(velGroup);

    // --- E. Cosmic Streamlines ---
    const streamGroup = new THREE.Group();
    if (effectiveData.streamlines && effectiveData.streamlines.length > 0) {
      effectiveData.streamlines.forEach((sl: any[]) => {
        const points = sl.map((p) => new THREE.Vector3(p.x, p.y, p.z));
        const curve = new THREE.CatmullRomCurve3(points);
        const tubeGeo = new THREE.TubeGeometry(curve, 32, 0.8, 6, false);
        const tubeMat = new THREE.MeshStandardMaterial({
          color: isDarkMode ? 0x34d399 : 0x059669,
          roughness: 0.4,
          clippingPlanes: [clipPlane],
        });
        const tube = new THREE.Mesh(tubeGeo, tubeMat);
        streamGroup.add(tube);
      });
    }
    streamGroup.visible = showStreamlines && (activeLayerMode === "SURVEY_BASE" || activeLayerMode === "PREDICTION");
    streamlinesGroupRef.current = streamGroup;
    scene.add(streamGroup);

    // --- F. Galaxy Markers ---
    const galGroup = new THREE.Group();
    if (effectiveData.galaxies && effectiveData.galaxies.length > 0) {
      effectiveData.galaxies.forEach((g: GalaxyItem) => {
        const geo = new THREE.SphereGeometry(g.is_holdout ? 3.6 : 2.8, 16, 16);
        const mat = new THREE.MeshStandardMaterial({
          color: g.is_holdout ? 0xf59e0b : 0x4f46e5,
          emissive: g.is_holdout ? 0xd97706 : 0x312e81,
          emissiveIntensity: 0.35,
          clippingPlanes: [clipPlane],
        });
        const sphere = new THREE.Mesh(geo, mat);
        sphere.position.set(g.x, g.y, g.z);
        sphere.userData = { galaxy: g };
        galGroup.add(sphere);
      });
    }
    galGroup.visible = showGalaxies;
    galaxiesGroupRef.current = galGroup;
    scene.add(galGroup);

    // --- G. Major Cosmic Attractor Annotations ---
    const annotGroup = new THREE.Group();
    if (effectiveData.attractors && effectiveData.attractors.length > 0) {
      effectiveData.attractors.forEach((att: any) => {
        const beaconGeo = new THREE.OctahedronGeometry(5.0, 0);
        const beaconMat = new THREE.MeshStandardMaterial({
          color: att.color || 0xdc2626,
          wireframe: true,
          clippingPlanes: [clipPlane],
        });
        const beacon = new THREE.Mesh(beaconGeo, beaconMat);
        beacon.position.set(att.x, att.y, att.z);
        annotGroup.add(beacon);
      });
    }
    annotGroup.visible = showAnnotations;
    annotationsGroupRef.current = annotGroup;
    scene.add(annotGroup);

    // =========================================================================
    // H. DIFFERENTIAL & RECONSTRUCTION VOXEL FIELDS (InstancedMesh 3D Sprites)
    // =========================================================================
    if (
      differentialData &&
      differentialData.voxels &&
      differentialData.voxels.length > 0 &&
      (activeLayerMode === "PREDICTION" || activeLayerMode === "HYBRID" || activeLayerMode === "DIFFERENTIAL")
    ) {
      const voxels = differentialData.voxels;
      const count = voxels.length;
      const boxSize = 8.5;
      const vGeo = new THREE.BoxGeometry(boxSize, boxSize, boxSize);
      const vMat = new THREE.MeshStandardMaterial({
        roughness: 0.45,
        metalness: 0.15,
        clippingPlanes: [clipPlane],
        transparent: true,
        opacity: isDarkMode ? 0.90 : 0.85,
      });

      const instMesh = new THREE.InstancedMesh(vGeo, vMat, count);
      const dummy = new THREE.Object3D();
      const color = new THREE.Color();

      const maxDelta = differentialData.summary.delta_density.max || 1.0;
      const minDelta = differentialData.summary.delta_density.min || -1.0;

      voxels.forEach((v, idx) => {
        dummy.position.set(v.x, v.y, v.z);

        if (activeLayerMode === "PREDICTION") {
          const norm = Math.min(1.0, Math.max(0, (v.pred_density + 1.0) / 4.0));
          if (v.pred_density > 1.0) {
            color.setRGB(0.96, 0.4 + (1 - norm) * 0.4, 0.1);
            dummy.scale.set(1.0, 1.0, 1.0);
          } else {
            color.setRGB(0.2, 0.35 + norm * 0.3, 0.65);
            dummy.scale.set(0.4, 0.4, 0.4);
          }
        } else if (activeLayerMode === "HYBRID") {
          const norm = Math.min(1.0, Math.max(0, (v.hybrid_density + 1.0) / 4.0));
          if (v.hybrid_density > 1.0) {
            color.setRGB(0.98, 0.35 + (1 - norm) * 0.3, 0.05);
            dummy.scale.set(1.05, 1.05, 1.05);
          } else {
            color.setRGB(0.18, 0.32 + norm * 0.3, 0.62);
            dummy.scale.set(0.4, 0.4, 0.4);
          }
        } else {
          // DIFFERENTIAL MODE: Diverging color palette
          const dd = v.delta_density;

          if (showInfoGainHighlight && v.info_gain_pct > 15.0) {
            color.setRGB(0.06, 0.85, 0.55); // Brilliant emerald
            dummy.scale.set(1.25, 1.25, 1.25);
          } else if (dd > 0.05) {
            const t = Math.min(1.0, dd / (maxDelta * 0.6 + 1e-4));
            color.setRGB(0.98, 0.65 - t * 0.45, 0.12);
            dummy.scale.set(Math.min(1.3, 0.6 + t * 0.7), Math.min(1.3, 0.6 + t * 0.7), Math.min(1.3, 0.6 + t * 0.7));
          } else if (dd < -0.05) {
            const t = Math.min(1.0, Math.abs(dd) / (Math.abs(minDelta) * 0.6 + 1e-4));
            color.setRGB(0.1 + (1 - t) * 0.1, 0.65 + t * 0.25, 0.95);
            dummy.scale.set(Math.min(1.2, 0.5 + t * 0.6), Math.min(1.2, 0.5 + t * 0.6), Math.min(1.2, 0.5 + t * 0.6));
          } else {
            color.setRGB(0.55, 0.60, 0.68);
            dummy.scale.set(0.25, 0.25, 0.25);
          }

          if (!showDiffDensity && !showInfoGainHighlight) {
            dummy.scale.set(0, 0, 0);
          }
        }

        dummy.updateMatrix();
        instMesh.setMatrixAt(idx, dummy.matrix);
        instMesh.setColorAt(idx, color);
      });

      instMesh.instanceMatrix.needsUpdate = true;
      if (instMesh.instanceColor) instMesh.instanceColor.needsUpdate = true;

      voxelMeshRef.current = instMesh;
      scene.add(instMesh);
    }

    // --- I. Differential Peculiar Velocity Arrows ---
    const diffVelGroup = new THREE.Group();
    if (
      activeLayerMode === "DIFFERENTIAL" &&
      showDiffVelocity &&
      differentialData &&
      differentialData.voxels
    ) {
      differentialData.voxels.forEach((v) => {
        if (v.delta_v_mag > 45) {
          const dir = new THREE.Vector3(v.delta_vx, v.delta_vy, v.delta_vz).normalize();
          const origin = new THREE.Vector3(v.x, v.y, v.z);
          const len = Math.min(Math.max(v.delta_v_mag * 0.032, 5), 22);
          const arrow = new THREE.ArrowHelper(dir, origin, len, 0xd946ef, 3.2, 2.0);
          diffVelGroup.add(arrow);
        }
      });
    }
    diffVelocityGroupRef.current = diffVelGroup;
    scene.add(diffVelGroup);

    // --- J. Revealed MeerKAT Holdout Points ---
    const holdoutGroup = new THREE.Group();
    const revealedTracers = differentialData?.holdout_galaxies || [];
    const canShowHoldout =
      (activeLayerMode === "HOLDOUT" || (activeLayerMode === "DIFFERENTIAL" && showRevealedHoldout)) &&
      differentialData?.holdout_authorized;

    if (canShowHoldout && revealedTracers.length > 0) {
      revealedTracers.forEach((g) => {
        const hGeo = new THREE.OctahedronGeometry(4.2, 0);
        const hMat = new THREE.MeshStandardMaterial({
          color: 0xf59e0b,
          emissive: 0xd97706,
          emissiveIntensity: 0.75,
          roughness: 0.3,
          clippingPlanes: [clipPlane],
        });
        const hMesh = new THREE.Mesh(hGeo, hMat);
        hMesh.position.set(g.x, g.y, g.z);
        hMesh.userData = { galaxy: g };
        holdoutGroup.add(hMesh);
      });
    }
    holdoutGroupRef.current = holdoutGroup;
    scene.add(holdoutGroup);

    // --- K. Selected Voxel 3D Highlight Bounding Box ---
    if (selectedVoxel) {
      const bGeo = new THREE.BoxGeometry(10.5, 10.5, 10.5);
      const bEdges = new THREE.EdgesGeometry(bGeo);
      const bMat = new THREE.LineBasicMaterial({
        color: 0x06b6d4,
        linewidth: 2,
        clippingPlanes: [clipPlane],
      });
      const highlightBox = new THREE.LineSegments(bEdges, bMat);
      highlightBox.position.set(selectedVoxel.x, selectedVoxel.y, selectedVoxel.z);
      voxelHighlightRef.current = highlightBox;
      scene.add(highlightBox);
    }
  }, [
    effectiveData,
    differentialData,
    activeLayerMode,
    showDiffDensity,
    showDiffVelocity,
    showInfoGainHighlight,
    showRevealedHoldout,
    sliceDepth,
    sliceAxis,
    isDarkMode,
    showHICloud,
    showCF4Velocity,
    showMilkyWayPlane,
    showStreamlines,
    showGalaxies,
    showGridAxes,
    showAnnotations,
    selectedVoxel,
  ]);

  // Camera Presets
  const applyCameraPreset = (preset: string) => {
    const cam = cameraRef.current;
    const ctrl = controlsRef.current;
    if (!cam || !ctrl) return;

    if (preset === "ALL_SKY") {
      cam.position.set(240, 190, 260);
      ctrl.target.set(0, 0, 0);
    } else if (preset === "OBSCURATION_SLICE") {
      cam.position.set(0, 320, 0);
      ctrl.target.set(0, 0, 0);
    } else if (preset === "VELA_SUPERCLUSTER" || preset === "DIFFERENTIAL_FOCUS") {
      cam.position.set(-140, -40, 90);
      ctrl.target.set(-140, -80, -5);
    } else if (preset === "GREAT_ATTRACTOR") {
      cam.position.set(-20, 50, 70);
      ctrl.target.set(-35, 15, -10);
    }
    ctrl.update();
  };

  const diffSummary = differentialData?.summary;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 360px",
        gap: "20px",
        height: "calc(100vh - 170px)",
        minHeight: "680px",
      }}
    >
      {/* Left: 3D Viewport */}
      <div
        style={{
          position: "relative",
          backgroundColor: isDarkMode ? "#0F172A" : "#FCFAF7",
          border: `2px solid ${isDarkMode ? "#334155" : "#E2E8F0"}`,
          borderRadius: "12px",
          overflow: "hidden",
          boxShadow: "inset 0 2px 8px rgba(0,0,0,0.04)",
        }}
      >
        {/* Top Floating Badge Bar */}
        <div
          style={{
            position: "absolute",
            top: 14,
            left: 16,
            zIndex: 10,
            display: "flex",
            gap: "10px",
            alignItems: "center",
          }}
        >
          <div
            style={{
              backgroundColor: isDarkMode ? "rgba(30, 41, 59, 0.9)" : "rgba(255, 255, 255, 0.94)",
              padding: "6px 12px",
              borderRadius: "6px",
              border: "1px solid rgba(148, 163, 184, 0.4)",
              backdropFilter: "blur(4px)",
              fontSize: "12px",
              fontWeight: 600,
              color: isDarkMode ? "#F8FAFC" : "#1E293B",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <span>3D COSMIC COMPANION</span>
            <span style={{ color: "#94A3B8" }}>&bull;</span>
            <span style={{ color: "#2563EB" }}>
              {activeLayerMode === "DIFFERENTIAL"
                ? "DIFFERENTIAL COMPARISON (Δδ / Δv / Δσ)"
                : activeLayerMode === "PREDICTION"
                ? "PREDICTION FIELD (WITHOUT HOLDOUT)"
                : activeLayerMode === "HYBRID"
                ? "HYBRID RECONSTRUCTION"
                : activeLayerMode === "HOLDOUT"
                ? "OBSERVED MEERKAT HOLDOUT"
                : "BASELINE SURVEY SPACE"}
            </span>
          </div>

          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            style={{
              padding: "6px 10px",
              borderRadius: "6px",
              border: "1px solid rgba(148, 163, 184, 0.4)",
              backgroundColor: isDarkMode ? "#1E293B" : "#FFFFFF",
              color: isDarkMode ? "#F8FAFC" : "#334155",
              fontSize: "11px",
              cursor: "pointer",
            }}
          >
            {isDarkMode ? "☀ Notebook Theme" : "🌙 Cosmic Dark"}
          </button>
        </div>

        {/* Loading Indicator */}
        {(loading || diffLoading) && (
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              zIndex: 20,
              color: isDarkMode ? "#94A3B8" : "#64748B",
              fontSize: "13px",
              fontWeight: 500,
              backgroundColor: isDarkMode ? "rgba(15, 23, 42, 0.8)" : "rgba(255, 255, 255, 0.85)",
              padding: "10px 18px",
              borderRadius: "8px",
              border: "1px solid #CBD5E1",
            }}
          >
            Loading differential fields &amp; 3D cosmic web...
          </div>
        )}

        {/* WebGL Canvas Container */}
        <div ref={mountRef} style={{ width: "100%", height: "100%" }} />

        {/* Interactive Galaxy Object Inspector */}
        {selectedObject && (
          <div
            style={{
              position: "absolute",
              bottom: 16,
              left: 16,
              zIndex: 15,
              backgroundColor: isDarkMode ? "rgba(15, 23, 42, 0.95)" : "rgba(255, 255, 255, 0.96)",
              border: `2px solid ${selectedObject.is_holdout ? "#F59E0B" : "#6366F1"}`,
              borderRadius: "8px",
              padding: "12px 16px",
              minWidth: "280px",
              boxShadow: "0 4px 14px rgba(0,0,0,0.12)",
              backdropFilter: "blur(6px)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <span style={{ fontWeight: 700, fontSize: "13px", color: selectedObject.is_holdout ? "#D97706" : "#4338CA" }}>
                {selectedObject.name}
              </span>
              <button
                onClick={() => setSelectedObject(null)}
                style={{ background: "none", border: "none", cursor: "pointer", color: "#94A3B8", fontSize: "14px" }}
              >
                ✕
              </button>
            </div>
            <div style={{ fontSize: "11px", color: isDarkMode ? "#CBD5E1" : "#475569", lineHeight: "1.6" }}>
              <div>ID: <span className="mono" style={{ fontWeight: 600 }}>{selectedObject.id}</span></div>
              <div>SGX: {selectedObject.x.toFixed(1)} Mpc &bull; SGY: {selectedObject.y.toFixed(1)} Mpc &bull; SGZ: {selectedObject.z.toFixed(1)} Mpc</div>
              <div>cz: <span className="mono">{selectedObject.cz} km/s</span> &bull; v_pec: <span className="mono" style={{ fontWeight: 600 }}>{selectedObject.v_pec > 0 ? `+${selectedObject.v_pec}` : selectedObject.v_pec} km/s</span></div>
              <div style={{ marginTop: "4px" }}>
                Role:{" "}
                <span
                  style={{
                    padding: "1px 6px",
                    borderRadius: "4px",
                    fontSize: "10px",
                    fontWeight: 600,
                    backgroundColor: selectedObject.is_holdout ? "#FEF3C7" : "#E0E7FF",
                    color: selectedObject.is_holdout ? "#92400E" : "#3730A3",
                  }}
                >
                  {selectedObject.is_holdout ? "MEERKAT HOLDOUT (REVEALED)" : "TRAINING SAMPLE"}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Clickable Voxel Inspector Overlay */}
        {selectedVoxel && (
          <div
            style={{
              position: "absolute",
              bottom: 16,
              left: 16,
              zIndex: 16,
              backgroundColor: isDarkMode ? "rgba(15, 23, 42, 0.96)" : "rgba(255, 255, 255, 0.98)",
              border: "2px solid #06B6D4",
              borderRadius: "8px",
              padding: "14px 16px",
              minWidth: "320px",
              boxShadow: "0 6px 20px rgba(0,0,0,0.18)",
              backdropFilter: "blur(8px)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "2px", backgroundColor: "#06B6D4" }} />
                <span style={{ fontWeight: 700, fontSize: "13px", color: isDarkMode ? "#F8FAFC" : "#0F172A" }}>
                  VOXEL INSPECTOR
                </span>
              </div>
              <button
                onClick={() => setSelectedVoxel(null)}
                style={{ background: "none", border: "none", cursor: "pointer", color: "#94A3B8", fontSize: "14px" }}
              >
                ✕
              </button>
            </div>

            <div style={{ fontSize: "11px", color: isDarkMode ? "#CBD5E1" : "#475569", lineHeight: "1.6" }}>
              <div style={{ padding: "4px 8px", backgroundColor: isDarkMode ? "#1E293B" : "#F1F5F9", borderRadius: "4px", marginBottom: "6px" }}>
                <strong>Voxel Coordinate:</strong> SGX: <span className="mono">{selectedVoxel.x.toFixed(1)}</span>, SGY: <span className="mono">{selectedVoxel.y.toFixed(1)}</span>, SGZ: <span className="mono">{selectedVoxel.z.toFixed(1)} Mpc</span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                <div style={{ border: "1px solid #E2E8F0", padding: "6px 8px", borderRadius: "4px" }}>
                  <div style={{ fontSize: "10px", color: "#64748B", textTransform: "uppercase" }}>Baseline Prediction</div>
                  <div style={{ fontWeight: 700, fontSize: "12px", color: "#2563EB" }}>
                    &delta; = {selectedVoxel.pred_density.toFixed(3)}
                  </div>
                  <div style={{ fontSize: "10px", color: "#94A3B8" }}>
                    &sigma; = &plusmn;{selectedVoxel.pred_sigma.toFixed(4)}
                  </div>
                </div>

                <div style={{ border: "1px solid #E2E8F0", padding: "6px 8px", borderRadius: "4px" }}>
                  <div style={{ fontSize: "10px", color: "#64748B", textTransform: "uppercase" }}>Hybrid Assimilation</div>
                  <div style={{ fontWeight: 700, fontSize: "12px", color: "#EA580C" }}>
                    &delta; = {selectedVoxel.hybrid_density.toFixed(3)}
                  </div>
                  <div style={{ fontSize: "10px", color: "#94A3B8" }}>
                    &sigma; = &plusmn;{selectedVoxel.hybrid_sigma.toFixed(4)}
                  </div>
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "4px", borderTop: "1px solid #E2E8F0", paddingTop: "6px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Net Density Shift (&Delta;&delta;):</span>
                  <span
                    className="mono"
                    style={{
                      fontWeight: 700,
                      color: selectedVoxel.delta_density >= 0 ? "#DC2626" : "#0284C7",
                    }}
                  >
                    {selectedVoxel.delta_density > 0 ? `+${selectedVoxel.delta_density.toFixed(4)}` : selectedVoxel.delta_density.toFixed(4)}
                  </span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Uncertainty Reduction (&Delta;&sigma;):</span>
                  <span className="mono" style={{ fontWeight: 600, color: "#059669" }}>
                    {selectedVoxel.delta_sigma.toFixed(5)}
                  </span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Information Gain (&Delta;&sigma; / &sigma;_pred):</span>
                  <span className="mono" style={{ fontWeight: 700, color: "#059669" }}>
                    +{selectedVoxel.info_gain_pct.toFixed(2)}%
                  </span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Differential Velocity Shift (&Delta;v):</span>
                  <span className="mono" style={{ fontWeight: 600, color: "#7C3AED" }}>
                    |&Delta;v| = {selectedVoxel.delta_v_mag.toFixed(1)} km/s
                  </span>
                </div>
              </div>

              <div
                style={{
                  marginTop: "8px",
                  fontSize: "9px",
                  fontWeight: 600,
                  color: "#059669",
                  backgroundColor: "#ECFDF5",
                  padding: "4px 8px",
                  borderRadius: "4px",
                  border: "1px solid #A7F3D0",
                  textAlign: "center",
                }}
              >
                🔒 STRICTLY READ-ONLY INTERACTION &bull; DOUBLE-BLIND ISOLATED
              </div>
            </div>
          </div>
        )}

        {/* Bottom Synchronized Slicing Controls Bar */}
        <div
          style={{
            position: "absolute",
            bottom: 16,
            right: 16,
            zIndex: 10,
            backgroundColor: isDarkMode ? "rgba(30, 41, 59, 0.92)" : "rgba(255, 255, 255, 0.95)",
            border: "1px solid rgba(148, 163, 184, 0.4)",
            borderRadius: "8px",
            padding: "8px 14px",
            display: "flex",
            alignItems: "center",
            gap: "12px",
            fontSize: "12px",
            backdropFilter: "blur(4px)",
          }}
        >
          <span style={{ fontWeight: 600, color: isDarkMode ? "#E2E8F0" : "#334155" }}>
            Synchronized Slice ({sliceAxis.toUpperCase()}):
          </span>
          <select
            value={sliceAxis}
            onChange={(e) => setSliceAxis(e.target.value as any)}
            style={{
              padding: "2px 6px",
              fontSize: "11px",
              borderRadius: "4px",
              border: "1px solid #CBD5E1",
              backgroundColor: isDarkMode ? "#1E293B" : "#FFFFFF",
              color: isDarkMode ? "#F8FAFC" : "#1E293B",
            }}
          >
            <option value="z">Z (Supergalactic Depth)</option>
            <option value="y">Y (Supergalactic North)</option>
            <option value="x">X (Line of Sight)</option>
          </select>
          <input
            type="range"
            min="-200"
            max="200"
            value={sliceDepth}
            onChange={(e) => setSliceDepth(parseFloat(e.target.value))}
            style={{ width: "110px", cursor: "pointer" }}
          />
          <span className="mono" style={{ fontSize: "11px", minWidth: "50px" }}>
            {sliceDepth > 0 ? `+${sliceDepth}` : sliceDepth} Mpc
          </span>
          <button
            onClick={() => setSliceDepth(200)}
            style={{
              padding: "2px 8px",
              fontSize: "10px",
              border: "1px solid #CBD5E1",
              borderRadius: "4px",
              backgroundColor: isDarkMode ? "#334155" : "#F1F5F9",
              cursor: "pointer",
            }}
          >
            Reset
          </button>
        </div>
      </div>

      {/* Right: Companion Sidebar Panel */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "14px",
          overflowY: "auto",
          paddingRight: "4px",
        }}
      >
        {/* Top Header Card */}
        <div
          style={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #E2E8F0",
            borderRadius: "8px",
            padding: "14px 16px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <h3 style={{ margin: 0, fontSize: "15px", fontWeight: 700, color: "#0F172A" }}>
              3D Lab Visualizer
            </h3>
            <span
              style={{
                fontSize: "10px",
                fontWeight: 600,
                padding: "2px 6px",
                borderRadius: "4px",
                backgroundColor: "#EFF6FF",
                color: "#1D4ED8",
                border: "1px solid #BFDBFE",
              }}
            >
              PAGE 4 &amp; 9
            </span>
          </div>
          <p style={{ margin: "6px 0 0 0", fontSize: "12px", color: "#64748B", lineHeight: "1.4" }}>
            Compare baseline predictions with the hybrid reconstruction and inspect differential fields (&Delta;&delta;, &Delta;v, &Delta;&sigma;) in real-time 3D.
          </p>
        </div>

        {/* Primary Layer Selection Tabs */}
        <div
          style={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #E2E8F0",
            borderRadius: "8px",
            padding: "12px 14px",
          }}
        >
          <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748B", marginBottom: "8px" }}>
            Reconstruction Layer Selection
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "6px" }}>
            <button
              onClick={() => setActiveLayerMode("DIFFERENTIAL")}
              style={{
                padding: "7px 10px",
                fontSize: "11px",
                fontWeight: activeLayerMode === "DIFFERENTIAL" ? 700 : 500,
                borderRadius: "6px",
                border: activeLayerMode === "DIFFERENTIAL" ? "2px solid #EA580C" : "1px solid #E2E8F0",
                backgroundColor: activeLayerMode === "DIFFERENTIAL" ? "#FFF7ED" : "#F8FAFC",
                color: activeLayerMode === "DIFFERENTIAL" ? "#C2410C" : "#1E293B",
                cursor: "pointer",
                textAlign: "left",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <span>⚡ Differential (&Delta;&delta; / &Delta;v / &Delta;&sigma;)</span>
              <span style={{ fontSize: "10px", color: "#EA580C", fontWeight: 600 }}>Active Diff</span>
            </button>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
              <button
                onClick={() => setActiveLayerMode("PREDICTION")}
                style={{
                  padding: "6px 8px",
                  fontSize: "11px",
                  fontWeight: activeLayerMode === "PREDICTION" ? 700 : 500,
                  borderRadius: "6px",
                  border: activeLayerMode === "PREDICTION" ? "2px solid #2563EB" : "1px solid #E2E8F0",
                  backgroundColor: activeLayerMode === "PREDICTION" ? "#EFF6FF" : "#F8FAFC",
                  color: activeLayerMode === "PREDICTION" ? "#1D4ED8" : "#1E293B",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                🔮 Prediction Field
              </button>

              <button
                onClick={() => setActiveLayerMode("HYBRID")}
                style={{
                  padding: "6px 8px",
                  fontSize: "11px",
                  fontWeight: activeLayerMode === "HYBRID" ? 700 : 500,
                  borderRadius: "6px",
                  border: activeLayerMode === "HYBRID" ? "2px solid #059669" : "1px solid #E2E8F0",
                  backgroundColor: activeLayerMode === "HYBRID" ? "#ECFDF5" : "#F8FAFC",
                  color: activeLayerMode === "HYBRID" ? "#047857" : "#1E293B",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                🧬 Hybrid Field
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
              <button
                onClick={() => setActiveLayerMode("HOLDOUT")}
                style={{
                  padding: "6px 8px",
                  fontSize: "11px",
                  fontWeight: activeLayerMode === "HOLDOUT" ? 700 : 500,
                  borderRadius: "6px",
                  border: activeLayerMode === "HOLDOUT" ? "2px solid #D97706" : "1px solid #E2E8F0",
                  backgroundColor: activeLayerMode === "HOLDOUT" ? "#FEF3C7" : "#F8FAFC",
                  color: activeLayerMode === "HOLDOUT" ? "#92400E" : "#1E293B",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                🔭 Observed Holdout
              </button>

              <button
                onClick={() => setActiveLayerMode("SURVEY_BASE")}
                style={{
                  padding: "6px 8px",
                  fontSize: "11px",
                  fontWeight: activeLayerMode === "SURVEY_BASE" ? 700 : 500,
                  borderRadius: "6px",
                  border: activeLayerMode === "SURVEY_BASE" ? "2px solid #64748B" : "1px solid #E2E8F0",
                  backgroundColor: activeLayerMode === "SURVEY_BASE" ? "#F1F5F9" : "#F8FAFC",
                  color: activeLayerMode === "SURVEY_BASE" ? "#0F172A" : "#1E293B",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                🌌 Survey Tracers
              </button>
            </div>
          </div>
        </div>

        {/* Differential Diagnostics & Layer Controls */}
        {activeLayerMode === "DIFFERENTIAL" && (
          <div
            style={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #FED7AA",
              borderRadius: "8px",
              padding: "14px",
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", color: "#C2410C" }}>
                Differential Controls
              </span>
              <span className="mono" style={{ fontSize: "10px", color: "#9A3412" }}>
                Run: {selectedRunId}
              </span>
            </div>

            {/* Differential Layer Toggles */}
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "11px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={showDiffDensity}
                  onChange={(e) => setShowDiffDensity(e.target.checked)}
                />
                <span style={{ display: "inline-block", width: "12px", height: "8px", borderRadius: "2px", background: "linear-gradient(to right, #06B6D4, #F59E0B)" }} />
                <span><strong>&Delta;&delta; Density Sprites:</strong> Cyan (&minus;) &harr; Orange (+)</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={showDiffVelocity}
                  onChange={(e) => setShowDiffVelocity(e.target.checked)}
                />
                <span style={{ display: "inline-block", width: "10px", height: "10px", borderRadius: "2px", backgroundColor: "#D946EF" }} />
                <span><strong>&Delta;v Velocity Vectors:</strong> Flow redirection</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={showInfoGainHighlight}
                  onChange={(e) => setShowInfoGainHighlight(e.target.checked)}
                />
                <span style={{ display: "inline-block", width: "10px", height: "10px", borderRadius: "2px", backgroundColor: "#10B981" }} />
                <span><strong>&Delta;&sigma; Information Gain:</strong> Highlight variance reduction</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={showRevealedHoldout}
                  onChange={(e) => setShowRevealedHoldout(e.target.checked)}
                />
                <span style={{ display: "inline-block", width: "10px", height: "10px", borderRadius: "2px", backgroundColor: "#F59E0B" }} />
                <span><strong>Revealed MeerKAT Tracers</strong> (39 Holdout Detections)</span>
              </label>
            </div>

            {/* Differential Numerical Summary Table */}
            {diffSummary && (
              <div
                style={{
                  marginTop: "6px",
                  padding: "8px 10px",
                  backgroundColor: "#FFFBEB",
                  border: "1px solid #FDE68A",
                  borderRadius: "6px",
                  fontSize: "11px",
                  color: "#92400E",
                  lineHeight: "1.5",
                }}
              >
                <div style={{ fontWeight: 700, marginBottom: "4px" }}>Scientific Field Differentials:</div>
                <div>&bull; Max &Delta;&delta; Node Sharpening: <strong className="mono">+{diffSummary.delta_density.max.toFixed(2)}</strong></div>
                <div>&bull; Min &Delta;&delta; Void Evacuation: <strong className="mono">{diffSummary.delta_density.min.toFixed(2)}</strong></div>
                <div>&bull; Max Uncertainty Reduction (&Delta;&sigma;): <strong className="mono">+{diffSummary.delta_sigma.max.toFixed(4)}</strong></div>
                <div>&bull; Mean Fractional Info Gain: <strong className="mono">+{diffSummary.mean_uncertainty_reduction_pct.toFixed(2)}%</strong></div>
                <div>&bull; Peculiar Velocity Shift RMS: <strong className="mono">{diffSummary.delta_velocity.rms.toFixed(1)} km/s</strong></div>
              </div>
            )}
          </div>
        )}

        {/* Camera Presets Card */}
        <div
          style={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #E2E8F0",
            borderRadius: "8px",
            padding: "12px 14px",
          }}
        >
          <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748B", marginBottom: "8px" }}>
            Camera Presets
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
            <button
              onClick={() => applyCameraPreset("ALL_SKY")}
              style={{
                padding: "5px 8px",
                fontSize: "11px",
                borderRadius: "4px",
                border: "1px solid #E2E8F0",
                backgroundColor: "#F8FAFC",
                color: "#1E293B",
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              🌌 All-Sky View
            </button>
            <button
              onClick={() => applyCameraPreset("OBSCURATION_SLICE")}
              style={{
                padding: "5px 8px",
                fontSize: "11px",
                borderRadius: "4px",
                border: "1px solid #E2E8F0",
                backgroundColor: "#F8FAFC",
                color: "#1E293B",
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              🌪 Obscuration Cut
            </button>
            <button
              onClick={() => applyCameraPreset("VELA_SUPERCLUSTER")}
              style={{
                padding: "5px 8px",
                fontSize: "11px",
                borderRadius: "4px",
                border: "1px solid #FED7AA",
                backgroundColor: "#FFF7ED",
                color: "#C2410C",
                fontWeight: 600,
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              ⭐ Vela Diff Focus
            </button>
            <button
              onClick={() => applyCameraPreset("GREAT_ATTRACTOR")}
              style={{
                padding: "5px 8px",
                fontSize: "11px",
                borderRadius: "4px",
                border: "1px solid #FECACA",
                backgroundColor: "#FEE2E2",
                color: "#991B1B",
                fontWeight: 600,
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              🎯 Great Attractor
            </button>
          </div>
        </div>

        {/* Standard Layers on/off panel */}
        <div
          style={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #E2E8F0",
            borderRadius: "8px",
            padding: "12px 14px",
          }}
        >
          <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748B", marginBottom: "8px" }}>
            Survey Reference Layers
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "11px" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input type="checkbox" checked={showHICloud} onChange={(e) => setShowHICloud(e.target.checked)} />
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#2563EB" }} />
              <span>H I Survey Points</span>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input type="checkbox" checked={showCF4Velocity} onChange={(e) => setShowCF4Velocity(e.target.checked)} />
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "2px", backgroundColor: "#E11D48" }} />
              <span>CF4 Velocities</span>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input type="checkbox" checked={showMilkyWayPlane} onChange={(e) => setShowMilkyWayPlane(e.target.checked)} />
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "2px", backgroundColor: "#A8A29E" }} />
              <span>Milky Way Mask (|b|&lt;10°)</span>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input type="checkbox" checked={showStreamlines} onChange={(e) => setShowStreamlines(e.target.checked)} />
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "2px", backgroundColor: "#059669" }} />
              <span>Cosmic Streamlines</span>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input type="checkbox" checked={showGalaxies} onChange={(e) => setShowGalaxies(e.target.checked)} />
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#4F46E5" }} />
              <span>Known Tracers</span>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input type="checkbox" checked={showGridAxes} onChange={(e) => setShowGridAxes(e.target.checked)} />
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "2px", backgroundColor: "#94A3B8" }} />
              <span>Bounding Box &amp; Axes</span>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input type="checkbox" checked={showAnnotations} onChange={(e) => setShowAnnotations(e.target.checked)} />
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "2px", backgroundColor: "#DC2626" }} />
              <span>Attractor Beacons (GA / Shapley / Vela)</span>
            </label>
          </div>
        </div>

        {/* Read-Only Safety & Navigation Card */}
        <div
          style={{
            backgroundColor: "#F8FAFC",
            border: "1px dashed #CBD5E1",
            borderRadius: "8px",
            padding: "12px",
            fontSize: "11px",
            color: "#475569",
          }}
        >
          <div style={{ fontWeight: 600, color: "#0F172A", marginBottom: "4px" }}>
            🔒 Read-Only Integrity Contract:
          </div>
          <p style={{ margin: 0, lineHeight: "1.4" }}>
            3D Lab interactions are strictly read-only. Adjusting camera, slicing planes, or inspecting voxels cannot mutate the paper&apos;s sealed validation report.
          </p>

          {onNavigateToCalc && (
            <button
              onClick={onNavigateToCalc}
              style={{
                marginTop: "10px",
                width: "100%",
                padding: "6px",
                fontSize: "11px",
                fontWeight: 600,
                backgroundColor: "#1E293B",
                color: "#FFFFFF",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              ← Back to White Calculation Room
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
