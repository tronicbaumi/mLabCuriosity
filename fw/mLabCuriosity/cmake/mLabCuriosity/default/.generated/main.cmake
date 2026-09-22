include("${CMAKE_CURRENT_LIST_DIR}/rule.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/file.cmake")

set(mLabCuriosity_default_library_list )

# Handle files with suffix s, for group default-XC-DSC
if(mLabCuriosity_default_default_XC_DSC_FILE_TYPE_assemble)
add_library(mLabCuriosity_default_default_XC_DSC_assemble OBJECT ${mLabCuriosity_default_default_XC_DSC_FILE_TYPE_assemble})
    mLabCuriosity_default_default_XC_DSC_assemble_rule(mLabCuriosity_default_default_XC_DSC_assemble)
    list(APPEND mLabCuriosity_default_library_list "$<TARGET_OBJECTS:mLabCuriosity_default_default_XC_DSC_assemble>")

endif()

# Handle files with suffix S, for group default-XC-DSC
if(mLabCuriosity_default_default_XC_DSC_FILE_TYPE_assemblePreproc)
add_library(mLabCuriosity_default_default_XC_DSC_assemblePreproc OBJECT ${mLabCuriosity_default_default_XC_DSC_FILE_TYPE_assemblePreproc})
    mLabCuriosity_default_default_XC_DSC_assemblePreproc_rule(mLabCuriosity_default_default_XC_DSC_assemblePreproc)
    list(APPEND mLabCuriosity_default_library_list "$<TARGET_OBJECTS:mLabCuriosity_default_default_XC_DSC_assemblePreproc>")

endif()

# Handle files with suffix c, for group default-XC-DSC
if(mLabCuriosity_default_default_XC_DSC_FILE_TYPE_compile)
add_library(mLabCuriosity_default_default_XC_DSC_compile OBJECT ${mLabCuriosity_default_default_XC_DSC_FILE_TYPE_compile})
    mLabCuriosity_default_default_XC_DSC_compile_rule(mLabCuriosity_default_default_XC_DSC_compile)
    list(APPEND mLabCuriosity_default_library_list "$<TARGET_OBJECTS:mLabCuriosity_default_default_XC_DSC_compile>")

endif()

# Handle files with suffix cpp, for group default-XC-DSC
if(mLabCuriosity_default_default_XC_DSC_FILE_TYPE_compile_cpp)
add_library(mLabCuriosity_default_default_XC_DSC_compile_cpp OBJECT ${mLabCuriosity_default_default_XC_DSC_FILE_TYPE_compile_cpp})
    mLabCuriosity_default_default_XC_DSC_compile_cpp_rule(mLabCuriosity_default_default_XC_DSC_compile_cpp)
    list(APPEND mLabCuriosity_default_library_list "$<TARGET_OBJECTS:mLabCuriosity_default_default_XC_DSC_compile_cpp>")

endif()

# Handle files with suffix s, for group default-XC-DSC
if(mLabCuriosity_default_default_XC_DSC_FILE_TYPE_dependentObject)
add_library(mLabCuriosity_default_default_XC_DSC_dependentObject OBJECT ${mLabCuriosity_default_default_XC_DSC_FILE_TYPE_dependentObject})
    mLabCuriosity_default_default_XC_DSC_dependentObject_rule(mLabCuriosity_default_default_XC_DSC_dependentObject)
    list(APPEND mLabCuriosity_default_library_list "$<TARGET_OBJECTS:mLabCuriosity_default_default_XC_DSC_dependentObject>")

endif()

# Handle files with suffix elf, for group default-XC-DSC
if(mLabCuriosity_default_default_XC_DSC_FILE_TYPE_bin2hex)
add_library(mLabCuriosity_default_default_XC_DSC_bin2hex OBJECT ${mLabCuriosity_default_default_XC_DSC_FILE_TYPE_bin2hex})
    mLabCuriosity_default_default_XC_DSC_bin2hex_rule(mLabCuriosity_default_default_XC_DSC_bin2hex)
    list(APPEND mLabCuriosity_default_library_list "$<TARGET_OBJECTS:mLabCuriosity_default_default_XC_DSC_bin2hex>")

endif()


# Main target for this project
add_executable(mLabCuriosity_default_image__L_givq0 ${mLabCuriosity_default_library_list})

if(NOT CMAKE_HOST_WIN32)
    set_target_properties(mLabCuriosity_default_image__L_givq0 PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${mLabCuriosity_default_output_dir}")
endif()
set_target_properties(mLabCuriosity_default_image__L_givq0 PROPERTIES
    OUTPUT_NAME "default"
    SUFFIX ".elf")
target_link_libraries(mLabCuriosity_default_image__L_givq0 PRIVATE ${mLabCuriosity_default_default_XC_DSC_FILE_TYPE_link})
# Add the link options from the rule file.
mLabCuriosity_default_link_rule( mLabCuriosity_default_image__L_givq0)

# Call bin2hex function from the rule file
mLabCuriosity_default_bin2hex_rule(mLabCuriosity_default_image__L_givq0)
if(CMAKE_HOST_WIN32)
    add_custom_command(
        TARGET mLabCuriosity_default_image__L_givq0
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory ${mLabCuriosity_default_output_dir}
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:mLabCuriosity_default_image__L_givq0> ${mLabCuriosity_default_output_dir}/${mLabCuriosity_default_original_image_name}
        BYPRODUCTS ${mLabCuriosity_default_output_dir}/${mLabCuriosity_default_original_image_name}
        COMMENT "Copying elf to out location")
    set_property(
        TARGET mLabCuriosity_default_image__L_givq0
        APPEND PROPERTY ADDITIONAL_CLEAN_FILES
        ${mLabCuriosity_default_output_dir}/${mLabCuriosity_default_original_image_name})
endif()


