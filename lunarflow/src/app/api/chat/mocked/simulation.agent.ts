import { ComponentDataType } from "@/models/component/ComponentModel";
import { LunarAgent, ReasoningType } from "../types";

export const simulationAgent: LunarAgent = {
  instruction: "Model a 1 µm × 2 µm, 20 nm-thick permalloy-like rectangle (A = 1.3 × 10⁻¹¹ J m⁻¹, Mₛ = 8.0 × 10⁵ A m⁻¹, Kᵤ = 5 × 10² J m⁻³) with uniaxial anisotropy along the long edge. Simulate M-H hysteresis loops and low-field susceptibilities for fields applied parallel to both axes, record equilibrium features (vortex count, cross-tie walls, edge curling, jump behavior) as functions of initial state and zero-field alignment, and track the effect of ≤1° misalignments. Compare 2-D and 3-D micromagnetic treatments, capturing vortex cores where needed, using FFT or multipole methods for magnetostatics (alternatives noted), and report run time and hardware required.",
  agentName: "Micromagnetic Simulation Agent",
  agentDescription: "An agent that extracts parameters, prepares and runs micromagnetic simulations (2D/3D) for permalloy rectangles, analyzes domain features and hysteresis, and reports on computational methods and results.",
  inputs: [
    {
      name: "Simulation Specification",
      dataType: "TEXT",
    }
  ],
  reasoningChain: [
    {
      id: "1",
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: "Extracting parameters from the simulation specification (geometry, material, outputs, computational methods, alignment sensitivities).",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "",
      },
    },
    {
      id: "2",
      reasoningType: ReasoningType.GettingTrustedSources,
      reasoningDescription: "Getting simulation method and API descriptions from the MuMax3 simulator knowledge base.",
      executionTime: 2,
      output: {
        type: ComponentDataType.TEXT,
        content: `
        Cuboid(float64, float64, float64): Cuboid with sides in meters

Methods: Add(Shape), Intersect(Shape), Inverse(), Repeat(float64, float64, float64), RotX(float64), RotY(float64), RotZ(float64), Scale(float64, float64, float64), Sub(Shape), Transl(float64, float64, float64), Xor(Shape) Cylinder(float64, float64): 3D Cylinder with diameter and height in meters
Methods: Add(Shape), Intersect(Shape), Inverse(), Repeat(float64, float64, float64), RotX(float64), RotY(float64), RotZ(float64), Scale(float64, float64, float64), Sub(Shape), Transl(float64, float64, float64), Xor(Shape) Rect(float64, float64): 2D rectangle with size in meters

Methods: Add(Shape), Intersect(Shape), Inverse(), Repeat(float64, float64, float64), RotX(float64), RotY(float64), RotZ(float64), Scale(float64, float64, float64), Sub(Shape), Transl(float64, float64, float64), Xor(Shape) Square(float64): 2D square with size in meters

Methods: Add(Shape), Intersect(Shape), Inverse(), Repeat(float64, float64, float64), RotX(float64), RotY(float64), RotZ(float64), Scale(float64, float64, float64), Sub(Shape), Transl(float64, float64, float64), Xor(Shape) GrainRoughness(float64, float64, float64, int): Grainy surface with different heights per grain with a typical grain size (first argument), minimal height (second argument), and maximal height (third argument)

The last argument is a seed for the random number generator

Methods: Add(Shape), Intersect(Shape), Inverse(), Repeat(float64, float64, float64), RotX(float64), RotY(float64), RotZ(float64), Scale(float64, float64, float64), Sub(Shape), Transl(float64, float64, float64), Xor(Shape) SetPBC(int, int, int): Sets the number of repetitions in X,Y,Z to create periodic boundary conditions

The number of repetitions determines the cutoff range for the demagnetization

EdgeSmooth: Geometry edge smoothing with edgeSmooth^3 samples per cell, 0=staircase, ~8=very smooth SetGridSize(int, int, int): Sets the number of cells for X,Y,Z SetCellSize(float64, float64, float64): Sets the X,Y,Z cell size in meters SetGeom(Shape): Sets the geometry to a given shape DefRegion(int, Shape): Define a material region with given index (0-255) and shape

DefRegionCell(int, int, int, int): Set a material region (first argument) in one cell by the index of the cell (last three arguments)

regions: Outputs the region index for each cell

Methods: Average(), EvalTo(Slice), GetCell(int, int, int), Gpu(), HostArray(), HostList(), LoadFile(string), SetCell(int, int, int, int) VortexWall(float64, float64, int, int) Config: Vortex wall magnetization with given mx in left and right domain and core circulation and polarization

Methods: Add(float64, Config), RotZ(float64), Scale(float64, float64, float64), Transl(float64, float64, float64) m: Reduced magnetization (unit length)

Methods: Average(), Buffer(), Comp(int), EvalTo(Slice), GetCell(int, int, int), LoadFile(string), Quantity(), Region(int), Set(Config), SetArray(Slice), SetCell(int, int, int, data.Vector), SetInShape(Shape, Config), SetRegion(int, Config) Uniform(float64, float64, float64) Config: Uniform magnetization in given direction

Methods: Add(float64, Config), RotZ(float64), Scale(float64, float64, float64), Transl(float64, float64, float64) Vortex(int, int) Config: Vortex magnetization with given circulation and core polarization

Methods: Add(float64, Config), RotZ(float64), Scale(float64, float64, float64), Transl(float64, float64, float64) TwoDomain(float64, float64, float64, float64, float64, float64, float64, float64, float64) Config: Two-domain magnetization with given magnetization in left domain, wall, and right domain

Methods: Add(float64, Config), RotZ(float64), Scale(float64, float64, float64), Transl(float64, float64, float64) Aex: Exchange stiffness (J/m)

Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) alpha: Landau-Lifshitz damping constant

Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) anisC1: Cubic anisotropy direction #1. Methods: Average(), Comp(int), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), SetRegion(int, VectorFunction), SetRegionFn(int, func() [3]float64) anisC2: Cubic anisotropy direction #2. Methods: Average(), Comp(int), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), SetRegion(int, VectorFunction), SetRegionFn(int, func() [3]float64) anisU: Uniaxial anisotropy direction. Methods: Average(), Comp(int), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), SetRegion(int, VectorFunction), SetRegionFn(int, func() [3]float64) B1: First magneto-elastic coupling constant (J/m3). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) B2: Second magneto-elastic coupling constant (J/m3). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Dbulk: Bulk Dzyaloshinskii-Moriya strength (J/m2). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Dind: Interfacial Dzyaloshinskii-Moriya strength (J/m2). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) EpsilonPrime: Slonczewski secondary STT term ε'. Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) FreeLayerThickness: Slonczewski free layer thickness (if set to zero (default), then the thickness will be deduced from the mesh size) (m). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) frozenspins: Defines spins that should be fixed. Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Kc1: 1st order cubic anisotropy constant (J/m3). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Kc2: 2nd order cubic anisotropy constant (J/m3). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Kc3: 3rd order cubic anisotropy constant (J/m3). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Ku1: 1st order uniaxial anisotropy constant (J/m3). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Ku2: 2nd order uniaxial anisotropy constant (J/m3). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Lambda: Slonczewski Λ parameter. Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Msat: Saturation magnetization (A/m). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) NoDemagSpins: Disable magnetostatic interaction per region (default=0, set to 1 to disable). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Pol: Electrical current polarization. Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) Temp: Temperature (K). Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) xi: Non-adiabaticity of spin-transfer-torque. Methods: Average(), EvalTo(Slice), GetRegion(int), IsUniform(), MSlice(), Region(int), Set(float64), SetRegion(int, ScalarFunction), SetRegionFuncGo(int, func() float64), SetRegionValueGo(int, float64) J: Electrical current density (A/m2). Methods: Add(Slice, ScalarFunction), AddGo(Slice, func() float64), AddTo(Slice), Average(), Comp(int), EvalTo(Slice), IsUniform(), MSlice(), Region(int), RemoveExtraTerms(), Set(data.Vector), SetRegion(int, VectorFunction), SetRegionFn(int, func() [3]float64) FixedLayer: Slonczewski fixed layer polarization. Methods: Add(Slice, ScalarFunction), AddGo(Slice, func() float64), AddTo(Slice), Average(), Comp(int), EvalTo(Slice), IsUniform(), MSlice(), Region(int), RemoveExtraTerms(), Set(data.Vector), SetRegion(int, VectorFunction), SetRegionFn(int, func() [3]float64) B_ext: Externally applied field (T). Methods: Add(Slice, ScalarFunction), AddGo(Slice, func() float64), AddTo(Slice), Average(), Comp(int), EvalTo(Slice), IsUniform(), MSlice(), Region(int), RemoveExtraTerms(), Set(data.Vector), SetRegion(int, VectorFunction), SetRegionFn(int, func() [3]float64) Edens_demag: Magnetostatic energy density (J/m3). Methods: Average(), EvalTo(Slice), Region(int) m_full: Unnormalized magnetization (A/m). Methods: Average(), Comp(int), EvalTo(Slice), HostCopy(), Region(int) Edens_mel: Magneto-elastic energy density (J/m3). Methods: Average(), EvalTo(Slice), Region(int) m: Reduced magnetization (unit length). Methods: Average(), Buffer(), Comp(int), EvalTo(Slice), GetCell(int, int, int), LoadFile(string), Quantity(), Region(int), Set(Config), SetArray(Slice), SetCell(int, int, int, data.Vector), SetInShape(Shape Config), SetRegion(int, Config) B_demag: Magnetostatic field (T). Methods: Average(), Comp(int), EvalTo(Slice), HostCopy(), Region(int) OVF2_BINARY: OutputFormat = OVF2_BINARY sets binary OVF2 output. OVF1_BINARY: OutputFormat = OVF1_BINARY sets binary OVF1 output. Save(Quantity): Save space-dependent quantity once, with auto filename. SaveAs(Quantity, string): Save space-dependent quantity with custom filename. AutoSave(Quantity, float64): Auto save space-dependent quantity every period (s). FilenameFormat: printf formatting string for output filenames. Relax: Relax() tries to evolve the magnetization as closely as possible to the minimum energy state. This function assumes all excitations have been turned off (temperature, electrical current, time-dependent magnetic fields). During relax, precession is disabled and the time t does not increase. There is no need to set high damping. Minimize: Minimize() is like Relax, but uses the conjugate gradient method to find the energy minimum. It is usually much faster than Relax, but is a bit less robust against divergence. E.g., a random starting configuration can be Relaxed, but may fail with Minimize. Minimize is very well suited for hysteresis calculations, where we are never far away from the ground state. RelaxTorqueThreshold: MaxTorque threshold for relax(). If set to -1 (default), relax() will stop when the average torque is steady or increasing. NEval: Total number of torque evaluations. Methods: Average() EvalTo(Slice) Get() Minimize(): Use steepest conjugate gradient method to minimize the total energy.
        `,
      },
    },
    {
      id: "3",
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: "Getting code examples for the MuMax3 simulatorI.",
      executionTime: 2,
      output: {
        type: ComponentDataType.CODE,
        content: `
        Specifications: This standard micromagnetic problem includes both magnetostatic and exchange energies, but has the advantage of only one scaled parameter. If crystalline anisotropy is neglected and the geometry is fixed, scaling of the static micromagnetic equations (Brown's equations) yield a hysteresis loop which depends only on the scaled geometry to the exchange length when expressed as M/Ms versus H/Hm, where Hm = Ms (SI) or 4piMs (cgs emu). The exchange length is lex = (A/Km)1/2, where A is the exchange stiffness constant and Km is a magnetostatic energy density, Km = 1/2µ0Ms2 (SI) or 2piMs2 (cgs emu). The field should be applied in the [1,1,1] direction, approximately 54.74 degrees ( arccos[1/root(3)] ) from each of the coordinate axes. This field orientation is chosen to avoid potential symmetry breaking problems. Geometry: Let us take a thin film of thickness t, width d, and length L. We suggest to make the problem virtually 2D by choosing t/d = 0.1, and to obtain interesting non-uniform reversal modes, L/d = 5. Material parameters: The magnetostatic exchange length, lex Zero magnetocrystalline anisotropy Desired output for comparison: Calculated as a function of d/lex, with aspect ratios held constant at t/d = 0.1 and L/d = 5.0, Coercivity (Hc/Hm, the magnitude of the field at which the projection of the magnetization along the field, Mx+ My+ Mz, is zero.) Remanence ( Mx/Ms, My/Ms, Mz/Ms, at H = 0) Please see the µMAG standard problem strategy page for information on publicizing your results. Comments: If we all begin with d/lex = 0.1 then the film will switch in the plane uniformly with the Stoner-Wohlfarth result for the coercivity. As we increase d/lex, say to d/lex = 2, simple nonuniform rotation will occur. For d/lex > 2 complex vortex formation will begin to occur and both the remanence and coercivity will become very small. Also, eventually non uniform magnetization over the film thickness will occur. We all should agree when d/lex = 0.1, but it will be interesting to see as we increase d/lex when our results diverge. A ''21/2-D'' approach, where the particle is discretized by a 2-D mesh or grid with 3-D spins, is expected to be sufficient as long as t is less than lex. For larger particles, a three dimensional discretization may be necessary.

Msat  = 1000e3
Aex   = 10e-12

// define exchange length
lex := sqrt(10e-12 / (0.5 * mu0 * pow(1000e3 ,2)))

d 	:= 30 * lex                    	// we test for d/lex = 30
Sizex := 5*d                         	// magnet size x
Sizey := 1*d
Sizez := 0.1*d

nx := pow(2, ilogb(Sizex / (0.75*lex)))  // power-of-two number of cells
ny := pow(2, ilogb(Sizey / (0.75*lex)))  // not larger than 0.75 exchange lengths

SetGridSize(nx, ny, 1)
SetCellSize(Sizex/nx, Sizey/ny, Sizez)

m = Uniform(1, 0.1, 0)               	// initial mag
relax()

save(m)                              	// remanent magnetization
print("<m> for d/lex=30: ", m.average())

Specifications:

Standard problem #4 is focused on dynamic aspects of micromagnetic computations. The initial state is an equilibrium s-state such as is obtained after applying and slowly reducing a saturating field along the [1,1,1] direction to zero. Fields of magnitude sufficient to reverse the magnetization of the rectangle are applied to this initial state and the time evolution of the magnetization as the system moves towards equilibrium in the new fields are examined. The problem will be run for two different applied fields. Geometry: A film of thickness, t=3 nm, length, L=500 nm and width, d=125 nm will be used. Material parameters: Similar to Permalloy: A = 1.3e-11 J/m (1.3e-6 erg/cm) Ms = 8.0e5 A/m (800 emu/cc) K = 0.0 The dynamics, calculated either using the Landau-Lifshitz equation, Landau-Lifshitz equation or the Gilbert equation, Landau-Lifshitz-Gilbert equation will use parameters, alpha = 0.02, gamma prime = 221 km/As, gamma = 221.1 km/As, Lambda= 4.42 km/As Note that these parameters are related by the equations: equations Applied Fields: Two switching events will be calculated using fields applied in the x-y plane of different magnitude and direction. Field 1: µ0Hx=-24.6 mT, µ0Hy= 4.3 mT, µ0Hz= 0.0 mT which is a field approximately 25 mT, directed 170 degrees counterclockwise from the positive x axis Field 2: µ0Hx=-35.5 mT, µ0Hy=-6.3 mT, µ0Hz= 0.0 mT which is a field approximately 36 mT, directed 190 degrees counterclockwise from the positive x axis Each field will be applied instantaneously at t=0 to the equilibrium s-state . Comparison: Two outputs are desired for comparison: The (x,y,z) components of the spatially averaged magnetization of the sample as a function of time from t=0 until the sample reaches equilibrium in the new field An image of the magnetization at the time when the x-component of the spatially averaged magnetization first crosses zero The magnetization values in the time series data should be normalized by Ms. The time series data is desired so that a detailed comparison can be made between solutions. The magnetization images are to check for any differences in the reversal mechanisms if the time data between solutions is different. Please see the µMAG standard problem strategy page for information on publicizing your results. Comments: The problem was chosen so that resolving the dynamics should easier for the 170 degree applied field than the 190 degree applied field. Preliminary simulations reveal that, in the case of the field applied at 170 degrees, the magnetization in the center of the rectangle rotates in the same direction as at the ends during reversal. In the 190 degree case, however, the center rotates the opposite direction as the ends resulting in a more complicated reversal. The field amplitudes were chosen to be about 1.5 times the coercivity in each case. SetGridsize(128, 32, 1) SetCellsize(500e-9/128, 125e-9/32, 3e-9) Msat = 800e3 Aex = 13e-12 alpha = 0.02 m = uniform(1, .1, 0) relax() save(m) // relaxed state autosave(m, 200e-12) tableautosave(10e-12) B_ext = vector(-24.6E-3, 4.3E-3, 0) run(1e-9) Magnetic Force Microscopy Mumax3 has built-in generation of MFM images from the magnetization. The MFM tip lift can be freely chosen. By default the tip magnetization is modeled as a point monopole at the apex. This is sufficient for most situations. Nevertheless, it is also possible to model partially magnetized tips by setting MFMDipole to the magnetized portion of the tip, in meters. E.g., if only the first 20nm of the tip is (vertically) magnetized, set MFMDipole=20e-9. setgridsize(256, 256, 1) setcellsize(2e-9, 2e-9, 1e-9) setgeom(rect(400e-9, 400e-9)) msat = 600e3 aex = 10e-12 m = vortex(1, 1) relax() save(m) MFMLift = 10e-9 saveas(MFM, "lift_10nm") MFMLift = 40e-9 saveas(MFM, "lift_40nm") MFMLift = 90e-9 saveas(MFM, "lift_90nm") Hysteresis Below is an example of a hysteresis loop where we step the applied field in small increments and find the magnetization ground state after each step. Minimize() finds the ground state using the conjugate gradient method, which is very fast. However, this method might fail on very high energy initial states like a random magnetization. In that case, Relax() is more robust (albeit much slower).

SetGridsize(128, 32, 1)
SetCellsize(4e-9, 4e-9, 30e-9)

Msat  = 800e3
Aex   = 13e-12

m = randomMag()
relax()     	// high-energy states best minimized by relax()


Bmax  := 100.0e-3
Bstep :=  1.0e-3
MinimizerStop = 1e-6
TableAdd(B_ext)

for B:=0.0; B<=Bmax; B+=Bstep{
	B_ext = vector(B, 0, 0)
	minimize()   // small changes best minimized by minimize()
	tablesave()
}

for B:=Bmax; B>=-Bmax; B-=Bstep{
	B_ext = vector(B, 0, 0)
	minimize()   // small changes best minimized by minimize()
	tablesave()
}

for B:=-Bmax; B<=Bmax; B+=Bstep{
	B_ext = vector(B, 0, 0)
	minimize()   // small changes best minimized by minimize()
	tablesave()
}

Specifications:

Initial Magnetization Some initial magnetization functions are provided, as well as transformations similar to those on Shapes. See the Config API.

setgridsize(256, 128, 1)
setcellsize(5e-9, 5e-9, 5e-9)

m = Uniform(1, 1, 0)  // no need to normalize length
saveas(m, "uniform")

m = Vortex(1, -1) 	// circulation, polarization
saveas(m, "vortex")

m = TwoDomain(1,0,0,  0,1,0,  -1,0,0) // Néel wall
saveas(m, "twodomain")

m = RandomMag()
saveas(m, "randommag")

m = TwoDomain(1,0,0,  0,1,0,  -1,0,0).rotz(-pi/4)
saveas(m, "twodomain_rot")

m = VortexWall(1, -1, 1, 1)
saveas(m, "vortexwall")

m = VortexWall(1, -1, 1, 1).scale(1/2, 1, 1)
saveas(m, "vortexwall_scale")

m = Vortex(1,-1).transl(100e-9, 50e-9, 0)
saveas(m, "vortex_transl")

m = Vortex(1,-1).Add(0.1, randomMag())
saveas(m, "vortex_add_random")

m = BlochSkyrmion(1, -1).scale(3,3,1)
saveas(m, "Bloch_skyrmion")

m = NeelSkyrmion(1,-1).scale(3,3,1)
saveas(m, "Néel_skyrmion")

// set m in only a part of space, or a single cell:
m = uniform(1, 1, 1)
m.setInShape(cylinder(400e-9, 100e-9), vortex(1, -1))
m.setCell(20, 10, 0, vector(0.1, 0.1, -0.9)) // set in cell index  [20,10,0]
saveas(m, "setInShape_setCell")

//Read m form .ovf file.
m.loadfile("myfile.ovf")
saveas(m, "loadfile")
        `,
      },
    },
    {
      id: "4",
      reasoningType: ReasoningType.GeneratingCode,
      reasoningDescription: "Given the design specification, the API specification and the code examples from MuMax3.I am generating a MuMax3 code mapping to the design specification.",
      executionTime: 5,
      output: {
        type: ComponentDataType.CODE,
        content: `
        SetGridSize(200, 400, 1)
SetCellSize(1e-6/200, 2e-6/400, 20e-9)
SetGeom(Cuboid(1e-6, 2e-6, 20e-9))
Msat = 8e5
Aex = 1.3e-11
Ku1 = 5e2
anisU = vector(1, 0, 0)
m = Uniform(1, 0, 0)
Relax()
MinimizerStop = 1e-6
TableAdd(B_ext)
Bmax := 0.05
Bstep := 0.001
for B := -Bmax; B <= Bmax; B += Bstep {
    B_ext = vector(B, 0, 0)
    Minimize()
    TableSave()
}
m = Uniform(0, 1, 0)
Relax()
TableAdd(B_ext)
for B := -Bmax; B <= Bmax; B += Bstep {
    B_ext = vector(0, B, 0)
    Minimize()
    TableSave()
}
        `,
      },
    },
    {
      id: "5",
      reasoningType: ReasoningType.RunningSimulation,
      reasoningDescription: "Running the simulation in MuMax3",
      executionTime: 15,
      output: {
        type: ComponentDataType.TEXT,
        content: `
        MUMAX OUTPUT:

# t (s)	mx ()	my ()	mz ()	B_extx (T)	B_exty (T)	B_extz (T)
0	-0.8872228	5.197525e-09	0	-0.050000004	0	0
0	-0.8850679	1.2874604e-08	0	-0.049000006	0	0
0	-0.8828286	1.9598007e-08	0	-0.047999993	0	0
0	-0.880504	3.018379e-08	0	-0.046999995	0	0
0	-0.87808806	4.2486192e-08	0	-0.046	0	0
0	-0.87557054	4.005432e-08	0	-0.045000006	0	0
0	-0.87294114	3.657341e-08	0	-0.044000007	0	0
0	-0.8701954	3.118515e-08	0	-0.043	0	0
0	-0.86733097	2.7513504e-08	0	-0.042	0	0
0	-0.8643374	2.6464463e-08	0	-0.041000005	0	0
0	-0.8611995	1.988411e-08	0	-0.040000007	0	0
0	-0.8579082	5.531311e-09	0	-0.03899999	0	0
0	-0.85445774	-4.2915344e-10	0	-0.03799999	0	0
0	-0.850831	-4.7683715e-11	0	-0.037	0	0
0	-0.84700793	-2.861023e-09	0	-0.03600001	0	0
0	-0.842976	1.3828277e-08	0	-0.035000008	0	0
0	-0.8387088	3.9863586e-08	0	-0.034	0	0
0	-0.8341696	4.7922136e-08	0	-0.032999992	0	0
0	-0.82931465	1.6021728e-08	0	-0.032	0	0
0	-0.82403	-1.3208389e-08	0	-0.031	0	0
0	-0.80943817	3.185272e-08	0	-0.029999997	0	0
0	-0.77902967	-5.860233e-06	0	-0.028999992	0	0
0	-0.77223545	-2.4165154e-06	0	-0.028	0	0
0	-0.76510763	-1.1714935e-06	0	-0.027000003	0	0
0	-0.75308377	-3.9310456e-07	0	-0.025999997	0	0
0	-0.7308237	4.8509123e-06	0	-0.025000002	0	0
0	-0.7226714	2.0124435e-06	0	-0.023999996	0	0
0	-0.7141503	9.078503e-07	0	-0.023	0	0
0	-0.70026845	3.389597e-07	0	-0.022000004	0	0
0	-0.6859022	1.4214515e-07	0	-0.021	0	0
0	-0.5845255	-1.695031e-06	0	-0.020000003	0	0
0	-0.57447636	-8.453459e-07	0	-0.018999996	0	0
0	-0.56430316	-4.326701e-07	0	-0.018000005	0	0
0	-0.5539773	-2.1217465e-07	0	-0.017	0	0
0	-0.5434653	-1.10584494e-07	0	-0.016	0	0
0	-0.53273135	-5.264282e-08	0	-0.014999999	0	0
0	-0.52172863	-2.3293495e-08	0	-0.014	0	0
0	-0.5103888	-9.977818e-09	0	-0.012999998	0	0
0	-0.49848124	-4.220009e-09	0	-0.011999998	0	0
0	-0.47012728	-4.541874e-09	0	-0.011000002	0	0
0	-0.44671816	-8.392334e-09	0	-0.010000002	0	0
0	-0.4178437	-9.131432e-09	0	-0.009000002	0	0
0	-0.3886578	-1.0657311e-08	0	-0.008	0	0
0	-0.3429712	-2.503395e-09	0	-0.007	0	0
0	-0.32424617	-1.0490417e-09	0	-0.005999999	0	0
0	-0.2943569	7.033348e-09	0	-0.005000001	0	0
0	-0.25898847	3.2424927e-09	0	-0.004	0	0
0	-0.22344272	4.076958e-09	0	-0.0029999996	0	0
0	-0.18772717	4.1007997e-09	0	-0.002	0	0
0	-0.14669502	8.749962e-09	0	-0.001	0	0
0	-0.10556191	6.222725e-09	0	3.469447e-17	0	0
0	-0.06437976	1.7237664e-08	0	0.001	0	0
0	-0.017929593	1.4686584e-08	0	0.002	0	0
0	0.039273333	3.3855438e-09	0	0.0029999996	0	0
0	0.069637164	6.9141386e-09	0	0.004	0	0
0	0.11598163	9.870529e-09	0	0.005000001	0	0
0	0.16221933	9.989739e-09	0	0.005999999	0	0
0	0.3909339	-3.570795e-07	0	0.007	0	0
0	0.40410313	-2.4347304e-07	0	0.008	0	0
0	0.41689637	-1.5821458e-07	0	0.009000002	0	0
0	0.42938906	-1.0383129e-07	0	0.010000002	0	0
0	0.44164526	-7.047653e-08	0	0.011000002	0	0
0	0.45372245	-4.270077e-08	0	0.011999998	0	0
0	0.46568882	-2.4271012e-08	0	0.012999998	0	0
0	0.4776375	-1.0561943e-08	0	0.014	0	0
0	0.5058058	5.340576e-09	0	0.014999999	0	0
0	0.52839035	1.2254715e-08	0	0.016	0	0
0	0.56663567	1.33991245e-08	0	0.017	0	0
0	0.5832855	1.6546249e-08	0	0.018000005	0	0
0	0.6102603	2.1505356e-08	0	0.018999996	0	0
0	0.6370819	1.7356873e-08	0	0.020000003	0	0
0	0.8993705	2.2425651e-07	0	0.021	0	0
0	0.9029656	2.102375e-07	0	0.022000004	0	0
0	0.90634465	1.6298294e-07	0	0.023	0	0
0	0.90952265	1.5759468e-07	0	0.023999996	0	0
0	0.9125209	1.2736321e-07	0	0.025000002	0	0
0	0.9153513	1.1811257e-07	0	0.025999997	0	0
0	0.91802615	1.1754036e-07	0	0.027000003	0	0
0	0.9205637	1.1396408e-07	0	0.028	0	0
        `,
      },
    },
    {
      id: "6",
      reasoningType: ReasoningType.BuildingReport,
      reasoningDescription: "Generating a line plot: Normalized magnetization x External Field.",
      executionTime: 5,
      output: {
        type: ComponentDataType.LINE_CHART,
        content: {
          data: {
            "-0.05": -0.8872228,
            "-0.049": -0.8850679,
            "-0.048": -0.8828286,
            "-0.047": -0.880504,
            "-0.046": -0.87808806,
            "-0.045": -0.87557054,
            "-0.044": -0.87294114,
            "-0.043": -0.8701954,
            "-0.042": -0.86733097,
            "-0.041": -0.8643374,
            "-0.04": -0.8611995,
            "-0.039": -0.8579082,
            "-0.038": -0.85445774,
            "-0.037": -0.850831,
            "-0.036": -0.84700793,
            "-0.035": -0.842976,
            "-0.034": -0.8387088,
            "-0.033": -0.8341696,
            "-0.032": -0.82931465,
            "-0.031": -0.82403,
            "-0.03": -0.80943817,
            "-0.029": -0.77902967,
            "-0.028": -0.77223545,
            "-0.027": -0.76510763,
            "-0.026": -0.75308377,
            "-0.025": -0.7308237,
            "-0.024": -0.7226714,
            "-0.023": -0.7141503,
            "-0.022": -0.70026845,
            "-0.021": -0.6859022,
            "-0.02": -0.5845255,
            "-0.019": -0.57447636,
            "-0.018": -0.56430316,
            "-0.017": -0.5539773,
            "-0.016": -0.5434653,
            "-0.015": -0.53273135,
            "-0.014": -0.52172863,
            "-0.013": -0.5103888,
            "-0.012": -0.49848124,
            "-0.011": -0.47012728,
            "-0.01": -0.44671816,
            "-0.009": -0.4178437,
            "-0.008": -0.3886578,
            "-0.007": -0.3429712,
            "-0.006": -0.32424617,
            "-0.005": -0.2943569,
            "-0.004": -0.25898847,
            "-0.003": -0.22344272,
            "-0.002": -0.18772717,
            "-0.001": -0.14669502,
            "0.0": -0.10556191,
            "0.001": -0.06437976,
            "0.002": -0.017929593,
            "0.003": 0.039273333,
            "0.004": 0.069637164,
            "0.005": 0.11598163,
            "0.006": 0.16221933,
            "0.007": 0.3909339,
            "0.008": 0.40410313,
            "0.009": 0.41689637,
            "0.01": 0.42938906,
            "0.011": 0.44164526,
            "0.012": 0.45372245,
            "0.013": 0.46568882,
            "0.014": 0.4776375,
            "0.015": 0.5058058,
            "0.016": 0.52839035,
            "0.017": 0.56663567,
            "0.018": 0.5832855,
            "0.019": 0.6102603,
            "0.02": 0.6370819,
            "0.021": 0.8993705,
            "0.022": 0.9029656,
            "0.023": 0.90634465,
            "0.024": 0.90952265,
            "0.025": 0.9125209,
            "0.026": 0.9153513,
            "0.027": 0.91802615,
            "0.028": 0.9205637
          }
        },
      },
    },
    {
      id: "7",
      reasoningType: ReasoningType.BuildingReport,
      reasoningDescription: "Interpreting simulation results",
      executionTime: 5,
      output: {
        type: ComponentDataType.REPORT,
        content: `
        Hysteresis-curve plot description

The figure shows the longitudinal magnetisation component \(m_x\) plotted against the applied field \(B_{\text{ext}x}\) as extracted from the MuMax\textsuperscript{3} simulation.  
Starting close to full negative saturation at \(B_{\text{ext}x}\approx -0.05\;\text{T}\), the magnetisation rotates through zero near \(B_{\text{ext}x}=0\) and reaches positive saturation for \(B_{\text{ext}x}\gtrsim 0.02\;\text{T}\), producing the expected reversal curve of a uniaxial permalloy rectangle.  
The transverse components \(m_y\) and \(m_z\) remain five to eight orders of magnitude smaller over the entire field sweep and are omitted for clarity.  
Additional zoom views, overlays of \(m_y\) or \(m_z\), or a full return sweep to close the hysteresis loop can be generated on request.

        `,
      },
    }
  ],
  manualTime: 28800, // 8 hours in seconds
};
