; modelling_center
; ############################################################################
; Author: Yu Kosaka (RCAST, U. Tokyo, Japan)
; IPCC AR6 Chapter 3
; ############################################################################
; Description
;
;    Outputs:
;
; History
;    20190316 kosa_yu: written.
;
; Required diag_script_info attributes (diagnostic specific)
;    none
;
; Optional diag_script_info attributes (diagnostic specific)
;
; ############################################################################

function get_modelling_center(model)
local center
begin
  if (model.eq."ACCESS-CM2") then
    center = "CSIRO-ARCCSS-BoM"
  elseif (model.eq."ACCESS-ESM1-5") then
    center = "CSIRO"
  elseif (model.eq."ARTS-2-3") then
    center = "UHH"
  elseif (model.eq."AWI-CM-1-1-HR") then
    center = "AWI"
  elseif (model.eq."AWI-CM-1-1-LR") then
    center = "AWI"
  elseif (model.eq."AWI-CM-1-1-MR") then
    center = "AWI"
  elseif (model.eq."AWI-ESM-1-1-LR") then
    center = "AWI"
  elseif (model.eq."BCC-CSM2-HR") then
    center = "BCC"
  elseif (model.eq."BCC-CSM2-MR") then
    center = "BCC"
  elseif (model.eq."BCC-ESM1") then
    center = "BCC"
  elseif (model.eq."BESM-2-7") then
    center = "INPE"
  elseif (model.eq."BNU-ESM-1-1") then
    center = "BNU"
  elseif (model.eq."CAMS-CSM1-0") then
    center = "CAMS"
  elseif (model.eq."CanESM5") then
    center = "CCCma"
  elseif (model.eq."CAS-ESM1-0") then
    center = "CAS"
  elseif (model.eq."CESM2") then
    center = "NCAR"
  elseif (model.eq."CESM2-SE") then
    center = "NCAR"
  elseif (model.eq."CESM2-WACCM") then
    center = "NCAR"
  elseif (model.eq."CIESM") then
    center = "THU"
  elseif (model.eq."CMCC-CM2-HR4") then
    center = "CMCC"
  elseif (model.eq."CMCC-CM2-HR5") then
    center = "CMCC"
  elseif (model.eq."CMCC-CM2-SR5") then
    center = "CMCC"
  elseif (model.eq."CMCC-CM2-VHR4") then
    center = "CMCC"
  elseif (model.eq."CMCC-ESM2-HR5") then
    center = "CMCC"
  elseif (model.eq."CMCC-ESM2-SR5") then
    center = "CMCC"
  elseif (model.eq."CNRM-CM6-1") then
    center = "CNRM-CERFACS"
  elseif (model.eq."CNRM-CM6-1-HR") then
    center = "CNRM-CERFACS"
  elseif (model.eq."CNRM-ESM2-1") then
    center = "CNRM-CERFACS"
  elseif (model.eq."CNRM-ESM2-1-HR") then
    center = "CNRM-CERFACS"
  elseif (model.eq."CSIRO-Mk3L-1-3") then
    center = "UTAS"
  elseif (model.eq."E3SM-1-0") then
    center = "E3SM-Project"
  elseif (model.eq."EC-Earth3-AerChem") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3-CC") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3-GrIS") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3-HR") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3-LR") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3P") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3P-HR") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3P-VHR") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3-Veg") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."EC-Earth3-Veg-LR") then
    center = "EC-Earth-Consortium"
  elseif (model.eq."ECMWF-IFS-HR") then
    center = "ECMWF"
  elseif (model.eq."ECMWF-IFS-LR") then
    center = "ECMWF"
  elseif (model.eq."ECMWF-IFS-MR") then
    center = "ECMWF"
  elseif (model.eq."EMAC-2-53-AerChem") then
    center = "MESSy-Consortium"
  elseif (model.eq."EMAC-2-53-Vol") then
    center = "MESSy-Consortium"
  elseif (model.eq."FGOALS-f3-H") then
    center = "CAS"
  elseif (model.eq."FGOALS-f3-L") then
    center = "CAS"
  elseif (model.eq."FGOALS-g3") then
    center = "CAS"
  elseif (model.eq."FIO-ESM-2-0") then
    center = "FIO-QLNM"
  elseif (model.eq."GFDL-AM4") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-CM4C192") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-CM4") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-ESM2M") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-ESM4") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-OM4p5B") then
    center = "NOAA-GFDL"
  elseif (model.eq."GISS-E2-1-G") then
    center = "NASA-GISS"
  elseif (model.eq."GISS-E2-1-G-CC") then
    center = "NASA-GISS"
  elseif (model.eq."GISS-E2-1-H") then
    center = "NASA-GISS"
  elseif (model.eq."GISS-E2-1-MA-G") then
    center = "NASA-GISS"
  elseif (model.eq."GISS-E3-G") then
    center = "NASA-GISS"
  elseif (model.eq."HadGEM3-GC31-HH") then
    center = (/"MOHC", "NERC"/)
  elseif (model.eq."HadGEM3-GC31-HM") then
    center = (/"MOHC", "NERC"/)
  elseif (model.eq."HadGEM3-GC31-LL") then
    center = "MOHC"
  elseif (model.eq."HadGEM3-GC31-LM") then
    center = "MOHC"
  elseif (model.eq."HadGEM3-GC31-MH") then
    center = "MOHC"
  elseif (model.eq."HadGEM3-GC31-MM") then
    center = "MOHC"
  elseif (model.eq."ICON-ESM-LR") then
    center = "MPI-M"
  elseif (model.eq."IITM-ESM") then
    center = "CCCR-IITM"
  elseif (model.eq."INM-CM4-8") then
    center = "INM"
  elseif (model.eq."INM-CM5-0") then
    center = "INM"
  elseif (model.eq."INM-CM5-H") then
    center = "INM"
  elseif (model.eq."IPSL-CM6A-ATM-HR") then
    center = "IPSL"
  elseif (model.eq."IPSL-CM6A-LR") then
    center = "IPSL"
  elseif (model.eq."KACE-1-0-G") then
    center = "NIMS-KMA"
  elseif (model.eq."KIOST-ESM") then
    center = "KIOST"
  elseif (model.eq."LBLRTM-12-8") then
    center = "AER"
  elseif (model.eq."MCM-UA-1-0") then
    center = "UA"
  elseif (model.eq."MIROC6") then
    center = "MIROC"
  elseif (model.eq."MIROC-ES2H") then
    center = "MIROC"
  elseif (model.eq."MIROC-ES2L") then
    center = "MIROC"
  elseif (model.eq."MPI-ESM-1-2-HAM") then
    center = "HAMMOZ-Consortium"
  elseif (model.eq."MPI-ESM1-2-HR") then
    center = (/"MPI-M", "DWD_DKRZ"/)
  elseif (model.eq."MPI-ESM1-2-LR") then
    center = "MPI-M_AWI"
  elseif (model.eq."MRI-AGCM3-2") then
    center = "MRI"
  elseif (model.eq."MRI-ESM2-0") then
    center = "MRI"
  elseif (model.eq."NESM3") then
    center = "NUIST"
  elseif (model.eq."NICAM16-7S") then
    center = "MIROC"
  elseif (model.eq."NICAM16-8S") then
    center = "MIROC"
  elseif (model.eq."NICAM16-9D-L78") then
    center = "MIROC"
  elseif (model.eq."NICAM16-9S") then
    center = "MIROC"
  elseif (model.eq."NorESM2-HH") then
    center = "NCC"
  elseif (model.eq."NorESM2-LMEC") then
    center = "NCC"
  elseif (model.eq."NorESM2-LME") then
    center = "NCC"
  elseif (model.eq."NorESM2-LM") then
    center = "NCC"
  elseif (model.eq."NorESM2-MH") then
    center = "NCC"
  elseif (model.eq."NorESM2-MM") then
    center = "NCC"
  elseif (model.eq."NorCPM1") then
    center = "NCC"
  elseif (model.eq."PCMDI-test-1-0") then
    center = "PCMDI"
  elseif (model.eq."RRTMG-LW-4-91") then
    center = "AER"
  elseif (model.eq."RRTMG-SW-4-02") then
    center = "AER"
  elseif (model.eq."RTE-RRTMGP-181204") then
    center = "AER"
  elseif (model.eq."SAM0-UNICON") then
    center = "SNU"
  elseif (model.eq."TaiESM1") then
    center = "AS-RCEC"
  elseif (model.eq."UKESM1-0-LL") then
    center = (/"MOHC", "NERC", "NIMS-KMA_NIWA"/)
  elseif (model.eq."UKESM1-0-MMh") then
    center = (/"MOHC", "NERC"/)
  elseif (model.eq."UofT-CCSM4") then
    center = "UofT"
  elseif (model.eq."VRESM-1-0") then
    center = "CSIR-CSIRO"
  elseif (model.eq."ACCESS1-0") then
    center = "CSIRO-BOM"
  elseif (model.eq."ACCESS1-3") then
    center = "CSIRO-BOM"
  elseif (model.eq."bcc-csm1-1") then
    center = "BCC"
  elseif (model.eq."bcc-csm1-1-m") then
    center = "BCC"
  elseif (model.eq."BNU-ESM") then
    center = "BNU"
  elseif (model.eq."CanAM4") then
    center = "CCCma"
  elseif (model.eq."CanCM4") then
    center = "CCCma"
  elseif (model.eq."CanESM2") then
    center = "CCCma"
  elseif (model.eq."CCSM4") then
    center = "NCAR"
  elseif (model.eq."CESM1-BGC") then
    center = "NSF-DOE-NCAR"
  elseif (model.eq."CESM1-CAM5") then
    center = "NSF-DOE-NCAR"
  elseif (model.eq."CESM1-CAM5-1-FV2") then
    center = "NSF-DOE-NCAR"
  elseif (model.eq."CESM1-FASTCHEM") then
    center = "NSF-DOE-NCAR"
  elseif (model.eq."CESM1-WACCM") then
    center = "NSF-DOE-NCAR"
  elseif (model.eq."CFSv2-2011") then
    center = "COLA-CFS_NOAA-NCEP"
  elseif (model.eq."CMCC-CESM") then
    center = "CMCC"
  elseif (model.eq."CMCC-CM") then
    center = "CMCC"
  elseif (model.eq."CMCC-CMS") then
    center = "CMCC"
  elseif (model.eq."CNRM-CM5") then
    center = "CNRM-CERFACS"
  elseif (model.eq."CNRM-CM5-2") then
    center = "CNRM-CERFACS"
  elseif (model.eq."CSIRO-Mk3-6-0") then
    center = "CSIRO-QCCCE"
  elseif (model.eq."CSIRO-Mk3L-1-2") then
    center = "UTAS"
  elseif (model.eq."EC-EARTH") then
    center = "ICHEC"
  elseif (model.eq."FGOALS-g2") then
    center = "LASG-CESS"
  elseif (model.eq."FGOALS-gl") then
    center = "LASG-IAP"
  elseif (model.eq."FGOALS-s2") then
    center = "LASG-IAP"
  elseif (model.eq."FIO-ESM") then
    center = "FIO"
  elseif (model.eq."fio-esm") then
    center = "FIO"
  elseif (model.eq."GEOS-5") then
    center = "NASA-GMAO"
  elseif (model.eq."GFDL-CM2p1") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-CM3") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-ESM2G") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-ESM2M") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-HIRAM-C180") then
    center = "NOAA-GFDL"
  elseif (model.eq."GFDL-HIRAM-C360") then
    center = "NOAA-GFDL"
  elseif (model.eq."GISS-E2-H") then
    center = "NASA-GISS"
  elseif (model.eq."GISS-E2-H-CC") then
    center = "NASA-GISS"
  elseif (model.eq."GISS-E2-R") then
    center = "NASA-GISS"
  elseif (model.eq."GISS-E2-R-CC") then
    center = "NASA-GISS"
  elseif (model.eq."HadCM3") then
    center = "MOHC"
  elseif (model.eq."HadGEM2-A") then
    center = "MOHC"
  elseif (model.eq."HadGEM2-AO") then
    center = "NIMR-KMA"
  elseif (model.eq."HadGEM2-CC") then
    center = "MOHC"
  elseif (model.eq."HadGEM2-ES") then
    center = (/"INPE", "MOHC"/)
  elseif (model.eq."inmcm4") then
    center = "INM"
  elseif (model.eq."IPSL-CM5A-LR") then
    center = "IPSL"
  elseif (model.eq."IPSL-CM5A-MR") then
    center = "IPSL"
  elseif (model.eq."IPSL-CM5B-LR") then
    center = "IPSL"
  elseif (model.eq."MIROC-ESM") then
    center = "MIROC"
  elseif (model.eq."MIROC-ESM-CHEM") then
    center = "MIROC"
  elseif (model.eq."MIROC4h") then
    center = "MIROC"
  elseif (model.eq."MIROC5") then
    center = "MIROC"
  elseif (model.eq."MPI-ESM-LR") then
    center = "MPI-M"
  elseif (model.eq."MPI-ESM-MR") then
    center = "MPI-M"
  elseif (model.eq."MPI-ESM-P") then
    center = "MPI-M"
  elseif (model.eq."MRI-AGCM3-2H") then
    center = "MRI"
  elseif (model.eq."MRI-AGCM3-2S") then
    center = "MRI"
  elseif (model.eq."MRI-CGCM3") then
    center = "MRI"
  elseif (model.eq."MRI-ESM1") then
    center = "MRI"
  elseif (model.eq."NICAM-09") then
    center = "NICAM"
  elseif (model.eq."NorESM1-M") then
    center = "NCC"
  elseif (model.eq."NorESM1-ME") then
    center = "NCC"
  else
    error_msg("f", DIAG_SCRIPT, "", "Unkown model: "+model)
  end if
  return(center)
end