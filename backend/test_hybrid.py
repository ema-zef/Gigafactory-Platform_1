from simulation.capacity import calculate_required_material_flow
p={
 'number_of_electrodes_in_cell':10,'cathode_length_m':.1,'cathode_width_m':.05,'cathode_coll_width_m':.06,
 'anode_length_m':.11,'anode_width_m':.05,'anode_coll_width_m':.06,
 'mass_load_cath_kg_m2':.1,'mass_load_anode_kg_m2':.1,'effective_parent_web_width_m':.72,
 'cathode_coll_kg_m2':.01,'anode_coll_kg_m2':.01,
 'cathode_solid_content_min_w%':60,'anode_solid_content_min_w%':60,
 'cathode_am_w%':90,'cathode_additive_w%':5,'cathode_binder_w%':5,
 'anode_am_w%':90,'anode_additive_w%':5,'anode_binder_w%':5,
 'electrolite_g_cell_min':20,'separator_g_cell_min':10,'housing_g_cell_min':30,'sealing_kg_cell':.001
}
def step(name,cat,mode='in_house',price=0):
 return dict(technology_id=1 if mode=='in_house' else None,technology_name=name,process=name,process_category=cat,quality_rate=98,execution_mode=mode,fee_eur_per_unit=price,input_material=name if mode=='purchased_intermediate' else None)
# In-house mixing -> outsourced coating -> in-house calendaring
r=calculate_required_material_flow(product=p,required_good_cells_day=1000,cathode_route=[step('Mixing','MASS'),step('Coating','ROLL','outsourced',.1),step('Calendering','ROLL')])
assert len(r['external_processing'])==1 and len(r['technologies'])==3
assert r['material_requirements']['cathode_active_material_kg']>0
# Purchased coated roll -> in-house slitting
r=calculate_required_material_flow(product=p,required_good_cells_day=1000,cathode_route=[step('Coated roll','ROLL','purchased_intermediate',.5),step('Slitting','ROLL')])
assert r['material_requirements']['cathode_collector_kg']==0
assert len(r['external_processing'])==1
# Purchased unfilled cells -> filling
r=calculate_required_material_flow(product=p,required_good_cells_day=1000,assembly_route=[step('Unfilled cell','CELL','purchased_intermediate',2),step('Electrolyte Filling','CELL')])
assert r['material_requirements']['electrolyte_kg']>0 and r['material_requirements']['separator_kg']==0
print('3 hybrid smoke tests passed')
