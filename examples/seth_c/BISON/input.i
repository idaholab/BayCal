############################## GLOBALPARAMETERS ################################
[GlobalParams]
  density = 10487.36
  order = SECOND
  family = LAGRANGE
#  energy_per_fission = 3.28451e-11  # J/fission
#  volumetric_locking_correction = false     #false
  displacements = disp_x
###  temperature = temperature
[]

################################### PROBLEM ####################################
[Problem]
  type = ReferenceResidualProblem
  acceptable_iterations = 40
  acceptable_multiplier = 10
  reference_vector = 'ref'
  extra_tag_vectors = 'ref'
[]

################################### MESH #######################################
[Mesh]
  [layered1D_mesh]
    type = Layered1DMeshGenerator
    slices_per_block = 10
    uniform_slice_heights = True
    include_fuel = True
    include_plenum = True
    include_lower_plenum = True

    fuel_height = 9.779e-2
    plenum_height = 0.029419
    lower_plenum_height = 0.0038146

    pellet_bottom_coor = 0.0038146
    pellet_outer_radius = 4.117e-3
    clad_gap_width = 61e-6
    clad_thickness = 572e-6

    nx_c = 5
    nx_p = 20
    clad_mesh_density = customize
    pellet_mesh_density = customize
  []
  patch_update_strategy = iteration     ###auto
  partitioner = centroid
  centroid_partitioner_direction = y
  coord_type = RZ
[]
[UserObjects]
  [pin_geometry]
    type = Layered1DFuelPinGeometry
    mesh_generator = layered1D_mesh
  []
[]

############################### VARIABLES ######################################
[Variables]
  [temperature]
    initial_condition = 299.15      ###300.0
  []
[]

################################ AUXVARIABLES ##################################
[AuxVariables]
#  [disp_y] ## Required for easier visualization in Paraview
#  []
#  [disp_z] ## Required for easier visualization in Paraview
#  []
#-------------------------Reference Residual Variables--------------------------
  [fast_neutron_flux]
    block = 'clad'
###    initial_condition = 0.0
  []
  [fast_neutron_fluence]
    block = 'clad'
###    initial_condition = 0.0
  []
  [gap_cond]
    order = CONSTANT
    family = MONOMIAL

  []
[]

################################# FUNCTIONS ####################################
[Functions]

#----------------------Dummy Burnup Function------------------------------------
  [dummy]
    type = ConstantFunction
    value = 0.0
  []
#--------------------------Rod Power History------------------------------------
  [reactor_specific_power]
    type = PiecewiseLinear
    data_file = reactor_power_condensed.csv
    format = columns
    scale_factor = 1.0  #PCF in W/gMW
  []

  [pcf]
    type = ConstantFunction
    value = 2.0855
  []

  [rod_specific_power]
    type = CompositeFunction
    functions = 'reactor_specific_power pcf'
    scale_factor = 1.0
  []

  [radial_peaking]
    type = PiecewiseLinear
    axis = x
    format = columns
    xy_data = '0.00041    0.93
               0.00124    0.94
               0.00206    0.96
               0.00289    1.00
               0.00371    1.05'
  []

  [q]
    type = CompositeFunction
    functions = 'rod_specific_power radial_peaking'
    scale_factor = 10487.36e3  #Density in g/m^3
  []

  [./fast_flux_history]
    type = PiecewiseLinear
    format = columns
    scale_factor = 0.0
    xy_data = '-100       0
                  0       0
                1e8       0'
  [../]

#-------------------------- heat transfer coefficient---------------------------

   [htc_calc]
     type = ParsedFunction
     symbol_names = 't_clad'
     symbol_values = 'Peak_Clad_Temp'
     expression = 0.9*(-8.26252e-12*(t_clad)^4+5.5e-8*(t_clad)^3-6e-5*(t_clad)^2+7.57517e-2*(t_clad)+18.89378)
   []
#-------------------------- Capsule Pressure---------------------------
  [pressure_ramp]          # inlet coolant pressure evolution
    type = PiecewiseLinear
    format = columns         #Pressure at MFC (12.2 psi, 5000ft)
    xy_data = '0          84307.6
               1000000    84307.6'
  []

  [clad_axial_pressure]
    type = CladdingAxialPressureFunction
    plenum_pressure = plenum_pressure
    coolant_pressure = pressure_ramp
    coolant_pressure_scaling_factor = 1
    fuel_pin_geometry = pin_geometry
  []
  [fuel_axial_pressure]
    type = ParsedFunction
    expression = plenum_pressure
    symbol_names = plenum_pressure
    symbol_values = plenum_pressure
  []

[]
################################# KERNELS ######################################
[Kernels]

  [heat]
    type = HeatConduction
    variable = temperature
    extra_vector_tags = 'ref'
  []

  [heat_ie]
    type = HeatConductionTimeDerivative
    variable = temperature
    extra_vector_tags = 'ref'
  []

  [heat_source_fuel]
    type = HeatSource
    variable = temperature
    block = fuel
    function = q
    extra_vector_tags = 'ref'
  []
[]
########################## TENSORMECHANICS #####################################
[Modules]
  [TensorMechanics]
    [Layered1DMaster]
      [fuel]
        block = fuel
        add_variables = true
        strain = FINITE
        add_scalar_variables = true
        out_of_plane_strain_name = strain_yy
        fuel_pin_geometry = pin_geometry
        eigenstrain_names = 'fuel_thermal_eigenstrain'
        generate_output = 'vonmises_stress
                           stress_xx
                           stress_yy
                           stress_zz
                           strain_xx
                           strain_yy
                           strain_zz'
        extra_vector_tags = 'ref'
        outputs = none
        group_scalar_vars_in_reference_residual = true
        mesh_generator = layered1D_mesh

        out_of_plane_pressure_function = fuel_axial_pressure
      []
      [clad]
        block = clad
        add_variables = true
        strain = FINITE
        add_scalar_variables = true
        out_of_plane_strain_name = strain_yy
        fuel_pin_geometry = pin_geometry
        eigenstrain_names = 'clad_thermal_eigenstrain'
        generate_output = 'vonmises_stress
		                   stress_xx
		                   stress_yy
		                   stress_zz
		                   strain_xx
		                   strain_yy
		                   strain_zz
		                   elastic_strain_xx
		                   elastic_strain_yy
		                   elastic_strain_zz'
        extra_vector_tags = 'ref'
        outputs = none
        group_scalar_vars_in_reference_residual = true
        mesh_generator = layered1D_mesh

		out_of_plane_pressure_function = clad_axial_pressure
      []
    []
  []
[]

############################ AUXKERNELS ########################################
[AuxKernels]
  [gap_conductance]
    type = MaterialRealAux
    property = gap_conductance
    variable = gap_cond
    boundary = 10
  []
  [fast_neutron_flux]
    type = FastNeutronFluxAux
    variable = fast_neutron_flux
    block = clad
    function = fast_flux_history
    execute_on = timestep_begin
  []

  [fast_neutron_fluence]
    type = FastNeutronFluenceAux
    variable = fast_neutron_fluence
    fast_neutron_flux = fast_neutron_flux
    execute_on = timestep_begin
  []
[]

######################### CONTACT ##############################################
[Contact]
  [pellet_clad_mechanical]
    primary = 5
    secondary = 10
    formulation = kinematic
    model = frictionless
#    normal_smoothing_distance = 0.1
    penalty = 1e7     ###1e9
  []
[]

[ThermalContact]
  [./thermal_contact]
    type = GapHeatTransferLWR
    variable = temperature
    gap_geometry_type = CYLINDER
    primary = 5 #Cladding interior
    secondary = 10 #Fuel pellet surface
    emissivity_primary = 0.8 #Emissivity for fuel
    emissivity_secondary = 0.325 #Emissivity for clad
    roughness_coef = 0.605
    roughness_secondary = 1.0e-6
    roughness_primary = 2.0e-6
    kennard_coefficient = 0.2173
    contact_coef = 12.32028
    gap_conductance_model = TOPTAN
    thermal_accommodation_model = TOPTAN
    jump_distance_model = TOPTAN
    gas_thermal_conductivity_model = DEFAULT
    meyer_hardness_model = DIRECT
    plenum_pressure = plenum_pressure
    contact_pressure = contact_pressure
    # initial_gas_fractions = '1 0 0 0 0 0 0 0 0 0'
    #initial_fractions = '1 0 0 0 0 0 0 0 0 0'
#    normal_smoothing_distance = 0.1
#    quadrature = true
#    order = SECOND
    warnings = true
  [../]
[]

######################## BOUNDARYCONDITIONS ####################################
[BCs]
#-------------------------Mechanical--------------------------------------------
  [no_x_all]
    type = DirichletBC
    variable = disp_x
    boundary = 12
    value = 0.0
  []
#----------------------------Thermal--------------------------------------------
  [cladding_temp]
    type = ConvectiveFluxFunction
    variable = temperature
    boundary = 2
    T_infinity = 300.0
    coefficient = htc_calc     ##1
  []

  [Pressure]
#  apply coolant pressure on clad outer walls
    [coolantPressure]
      boundary = 2
      factor = 1
      function = pressure_ramp
    []
  []

  [PlenumPressure]
#  apply plenum pressure on clad inner walls and pellet surfaces
    [plenumPressure]
      boundary = 9
      initial_temperature = 293.15
      initial_pressure = 84307.6     #Pressure at MFC (12.2 psi, 5000ft)
      startup_time = 0.0
      R = 8.3143
      output_initial_moles = initial_moles       # coupling to post processor to get inital fill gas mass
      temperature = plenum_temp            # coupling to post processor to get gas temperature approximation
#      temperature = ave_temp_interior            # coupling to post processor to get gas temperature approximation
      volume = gas_volume                        # coupling to post processor to get gas volume
      #material_input = fis_gas_released          # coupling to post processor to get fission gas added
      output = plenum_pressure                   # coupling to post processor to output plenum/gap pressure
      displacements = 'disp_x'
    []
  []
[]

[LayeredPlenumTemperature]
  [plenum_temp]
    boundary = 5
    fuel_pin_geometry = pin_geometry
    inner_surfaces = '5'
    outer_surfaces = '10'
    temperature = temperature
    out_of_plane_strain = strain_yy
  []
[]

############################ MATERIALS #########################################
[Materials]
#----------------------------Fuel-----------------------------------------------
  [fuel_density]
    type = Density
    block = fuel
  []
#----------------------------Thermal--------------------------------------------
  [fuel_thermal]
    type = UO2Thermal
    block = fuel
    thermal_conductivity_model = FINK_LUCUTA
    burnup_function = dummy
    temperature = temperature
    initial_porosity = 0.05
    thermal_conductivity_scale_factor = 1.0
    specific_heat_scale_factor = 1.0
  []
#---------------------------Tensor Mechanics------------------------------------
  [fuel_elastic_stress]
    type = ComputeFiniteStrainElasticStress
    block = fuel
  []

  [fuel_elasticity_tensor]
    type = UO2ElasticityTensor
    block = fuel
    matpro_poissons_ratio = false
    matpro_youngs_modulus = true
    temperature = temperature
  []
#----------------------Eigenstrains---------------------------------------------
  [fuel_thermal_expansion]
    type = UO2ThermalExpansionMATPROEigenstrain
    temperature = temperature
    eigenstrain_name = fuel_thermal_eigenstrain
    stress_free_temperature = 300.0
  []
#--------------------Cladding---------------------------------------------------
  [clad_density]
    type = Density
    block = clad
    density = 6511.0
  []
#------------------Thermal------------------------------------------------------
  [clad_thermal]
    type = ZryThermal
    temperature = temperature
    block = clad
    zry_thermal_properties_model = MATPRO
    thermal_conductivity_scale_factor = 1.0
    specific_heat_scale_factor = 1.0
  []
#------------------Tensor Mechanics---------------------------------------------
  [clad_stress]
    type = ComputeFiniteStrainElasticStress
    block = clad
  []

  [clad_elasticity_tensor]
    type = ZryElasticityTensor
    block = clad
    temperature = temperature
    matpro_poissons_ratio = false
    matpro_youngs_modulus = false
#    cold_work_factor = 0.5
#    fast_neutron_fluence = fast_neutron_fluence
  []
#---------------------Eigenstrains----------------------------------------------
  [clad_thermal_expansion]
    type = ZryThermalExpansionMATPROEigenstrain
    block = 'clad'
    temperature = temperature
    stress_free_temperature = 300.0
    eigenstrain_name = clad_thermal_eigenstrain
  []
[]
####################### DAMPERS ################################################
[Dampers]
###  [limitT]
###    type = MaxIncrement
###    max_increment = 100.0
###    variable = temperature
###  []

  [limitX]
    type = MaxIncrement
    max_increment = 1e-3     ###5e-3
    variable = disp_x
  []
  [BoundingValueNodalDamper]
     type = BoundingValueNodalDamper
     max_value = 3200           # The maximum permissible iterative value for the variable.
     min_value = 200               # The minimum permissible iterative value for the variable.
     variable = temperature             # The name of the variable that this damper operates on
  []
[]

####################### EXECUTIONER ############################################

[Executioner]
  type = Transient
###  solve_type = 'PJFNK'

  petsc_options = '-snes_ksp_ew'
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
  petsc_options_value = 'lu superlu_dist'
  line_search = 'none'
  verbose = true
  l_max_its = 100
  l_tol = 1e-3     #10e-2

  nl_max_its = 50     #40
  nl_rel_tol = 1e-4     #1e-3
  nl_abs_tol = 1e-10     #1e-8

  start_time = 0
  end_time = 60

  dtmax = 1
  dtmin = 1e-7

  [TimeStepper]
    type = CSVTimeSequenceStepper
    file_name = relap_timesteps.csv
    column_name = time
    cutback_factor_at_failure = 0.5
  []

#  [TimeStepper]
#    type = IterationAdaptiveDT
#    dt = 0.1
#    force_step_every_function_point = true     #false
#    max_function_change = 2000     #150     #20
#    timestep_limiting_function = reactor_specific_power
#    optimal_iterations = 20
#    iteration_window = 5
#    linear_iteration_ratio = 100
#    growth_factor = 2.0
#  []
[]

######################### POSTPROCESSORS #######################################

[Postprocessors]
  [0_dt]
    type = TimestepSize
  []
  [ave_temp_interior]            # average temperature of the cladding interior and all pellet exteriors
    type = LayeredSideAverageValuePostprocessor
    boundary = 9
    variable = temperature
    execute_on = 'initial linear'
    fuel_pin_geometry = pin_geometry
  []
#  [clad_inner_vol]
#    type = LayeredInternalVolumePostprocessor
#    boundary = 7
#    component = 0
#    fuel_pin_geometry = pin_geometry
#    out_of_plane_strain = strain_yy
#    execute_on = 'initial linear'
#  []
#  [pellet_volume]
#    type = LayeredInternalVolumePostprocessor
#    boundary = 8
#    component = 0
#    fuel_pin_geometry = pin_geometry
#    out_of_plane_strain = strain_yy
#    execute_on = 'initial linear'
#  []
  [gas_volume]                # gas volume
    type = LayeredInternalVolumePostprocessor
    boundary = 9
    execute_on = 'initial linear'
    component = 0
    out_of_plane_strain = strain_yy
    fuel_pin_geometry = pin_geometry
  []
  [gap_cond_avg]
    type = SideAverageValue
    variable = gap_cond
    boundary = 10
    execute_on = 'initial TIMESTEP_END'
  []
  [gap_cond]
    type = ElementalVariableValue
    variable = gap_cond
    elementid = 139
    use_displaced_mesh = true
    execute_on = 'initial TIMESTEP_END'
  []
#-----------------------Used Above----------------------------------------------
# [material_timestep]
#     type = MaterialTimeStepPostprocessor
#     block = clad
#  []


#----------------------Heat Transfer Calculation--------------------------------
   [htc_calc]
     type = FunctionValuePostprocessor
     function = htc_calc
   []

#----------------------------Contact--------------------------------------------

  [contact_pressure]
    type = NodalExtremeValue
    variable = contact_pressure
    boundary = 5
    value_type = 'max'
  []

#---------------------------Power & Burnup--------------------------------------

  [rod_specific_power]
    type = FunctionValuePostprocessor
    function = rod_specific_power
  []

#  [radial_average_enthalpy]
#    type = RadialAverageEnthalpy
#    vectorpostprocessor = rad_temp
#    r_dim = x
#    fuel_type = UO2
#    outputs = no_print
#  []

#--------------------------Cladding Temperatures--------------------------------

  [clad_temp_OD]
    type = NodalVariableValue
    nodeid = 53
    variable = temperature
    execute_on = 'initial TIMESTEP_END'
  []

  [clad_temp_ID]
    type = NodalVariableValue
    nodeid = 44
    variable = temperature
    execute_on = 'initial TIMESTEP_END'
  []

  [Peak_Clad_Temp]
    type = NodalExtremeValue
    ##block = clad
    variable = temperature
    boundary = 2
    value_type = 'max'
    execute_on = 'initial linear'
  []

#------------------------Fuel Temperatures--------------------------------------

  [Peak_Fuel_Temp]
    type = NodalExtremeValue
    block = fuel
    variable = temperature
    value_type = max
    execute_on = 'initial TIMESTEP_END'
  []

  [fuel_temp_centerline]
    type = NodalVariableValue
    nodeid = 255
    variable = temperature
    execute_on = 'initial TIMESTEP_END'
  []

  [fuel_temp_surface]
    type = NodalVariableValue
    nodeid = 294
    variable = temperature
    execute_on = 'initial TIMESTEP_END'
  []

#---------------------Mechanical------------------------------------------------

  [gap_width]
    type = NodalVariableValue
    variable = penetration
    nodeid = 294
    use_displaced_mesh = True
    scale_factor = -1e6
    execute_on = 'initial TIMESTEP_END'
  []
#  [hoop_stress_clad_OD]
#    type = ElementalVariableValue
#    elementid = 539
#    variable = stress_zz
#  []

#  [vonmises_stress_clad_OD]
#    type = ElementalVariableValue
#    elementid = 539
#    variable = vonmises_stress
#  []

#  [hoop_strain_clad_OD]
#    type = ElementalVariableValue
#    elementid = 539
#    variable = strain_zz
#  []

#  [hoop_plastic_strain_clad_OD]
#    type = ElementalVariableValue
#    elementid = 329
#    variable = plastic_strain_zz
#  []

#  [axial_stress_clad_OD]
#    type = ElementalVariableValue
#    elementid = 539
#    variable = stress_yy
#  []

#  [axial_strain_clad_OD]
#    type = ElementalVariableValue
#    elementid = 539
#    variable = strain_yy
#  []

#  [axial_plastic_strain_clad_OD]
#    type = ElementalVariableValue
#    elementid = 329
#    variable = plastic_strain_yy
#  []

[]

########################### VECTOR POST PROCESSORS #############################

#[VectorPostprocessors]

#-------------------------- Radial  Profile ------------------------------------

#  [rad_temp]
#    type = LineValueSampler
#    start_point = '0.0  0.1  0.0'
#    end_point = '4.117e-3 0.1 0.0'
#    sort_by = x
#    variable = temperature
#    execute_on = timestep_end
#    num_points = 81
#    outputs = no_print
#  []

#  [rad_stress]
#    type = LineValueSampler
#    start_point = '0.0  0.07588  0.0'
#    end_point = '4.0963e-3 0.07588 0.0'
#    sort_by = x
#    variable = stress_zz
#    execute_on = timestep_end
#    num_points = 31
#    outputs = rad_temp
#  []

#[]

############################## OUTPUT ##########################################
[Outputs]
# Define output file(s)
  interval = 1
  exodus = false
  csv = true
#  print_linear_residuals = true
#  perf_graph = true
  color = false

#  [console]
#    type = Console
#    max_rows = 25
#  []

#  [exodus]
#    type = Exodus
#    interval = 3
#  []

[]

############################ DEBUG #############################################
#[Debug]
#  show_var_residual = 'disp_x temperature'
#  show_var_residual_norms = true
#  show_material_props = true
#[]
