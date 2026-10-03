set(DEPENDENT_MP_BIN2HEXmLabCuriosity_default__L_givq0 "c:/Program Files/Microchip/xc-dsc/v4.00/bin/xc-dsc-bin2hex.exe")
set(DEPENDENT_DEPENDENT_TARGET_ELFmLabCuriosity_default__L_givq0 ${CMAKE_CURRENT_LIST_DIR}/../../../../out/mLabCuriosity/default.elf)
set(DEPENDENT_TARGET_DIRmLabCuriosity_default__L_givq0 ${CMAKE_CURRENT_LIST_DIR}/../../../../out/mLabCuriosity)
set(DEPENDENT_BYPRODUCTSmLabCuriosity_default__L_givq0 ${DEPENDENT_TARGET_DIRmLabCuriosity_default__L_givq0}/${sourceFileNamemLabCuriosity_default__L_givq0}.s)
add_custom_command(
    OUTPUT ${DEPENDENT_TARGET_DIRmLabCuriosity_default__L_givq0}/${sourceFileNamemLabCuriosity_default__L_givq0}.s
    COMMAND ${DEPENDENT_MP_BIN2HEXmLabCuriosity_default__L_givq0} ${DEPENDENT_DEPENDENT_TARGET_ELFmLabCuriosity_default__L_givq0} --image ${sourceFileNamemLabCuriosity_default__L_givq0} ${addressmLabCuriosity_default__L_givq0} ${modemLabCuriosity_default__L_givq0} -mdfp=C:/Users/Chris/.mchp_packs/Microchip/dsPIC33AK-MP_DFP/1.6.273/xc16 
    WORKING_DIRECTORY ${DEPENDENT_TARGET_DIRmLabCuriosity_default__L_givq0}
    DEPENDS ${DEPENDENT_DEPENDENT_TARGET_ELFmLabCuriosity_default__L_givq0})
add_custom_target(
    dependent_produced_source_artifactmLabCuriosity_default__L_givq0 
    DEPENDS ${DEPENDENT_TARGET_DIRmLabCuriosity_default__L_givq0}/${sourceFileNamemLabCuriosity_default__L_givq0}.s
    )
