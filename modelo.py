"""Modelo económico del biosimilar de luspatercept (EE. UU.).

Es el mismo código que corre en el navegador dentro de index.html.
Uso: python modelo.py  -> imprime los cuatro escenarios de la planilla.
"""
import json, math

def _fl(x): return math.floor(round(x, 9))
def _ce(x): return math.ceil(round(x, 9))

DEFAULTS = dict(
    ventas_globales=4000e6, ventas_eeuu_2025=1888e6, ventas_global_2025=2327e6,
    cuota=0.20, cuota_inicial=0.20, anios_rampa=0, rampa_cuotas='5,10,15,20',
    precio_25=4188.0, precio_75=12548.0, neto_lista=1.0, peso=84.1, dosis=1.0, intervalo=21.0,
    precio_rel=0.60, caida_precio=0.0,
    usar_fraccion=False, fraccion_directa=0.20, rec_disp=0.25, rec_dist=0.16, rec_com=0.80,
    cosecha=500.0, titulo=1.25, rec_dsp=0.60, rec_llenado=0.95, reserva=0.05,
    dias_lote=11.0, dias_prep=7.0, dias_disp=300.0,
    mat_lote=350000.0, ensayos_lote=25000.0, ff_vial=50.0, ff_campana=25000.0, viales_campana=6000.0,
    op_planta=300000.0, logistica=0.01,
    sueldo=1500.0, meses=12.0, cargas=0.35, pers_des=5, pers_bio=15, pers_gmp=30,
    d_linea=500000.0, d_proceso=1500000.0, d_biosim=2000000.0, d_valid=1500000.0, d_ff=500000.0, d_regul=500000.0,
    programa_clinico='completo', clinica_completa=150e6, clinica_abreviada=50e6, inicio_clinica=2032, anios_clinica=3,
    inicio=2028, lanzamiento=2036, fin=2041,
    tasa=0.10, impuesto=0.35, quebrantos=0, ct_dias=60.0,
)

def _irr(fl):
    def npv(r): return sum(v/(1+r)**t for t, v in enumerate(fl))
    lo, hi = -0.99, 10.0
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo*f_hi > 0: return None
    for _ in range(300):
        mid = (lo+hi)/2; f_m = npv(mid)
        if f_lo*f_m <= 0: hi, f_hi = mid, f_m
        else: lo, f_lo = mid, f_m
    return (lo+hi)/2

def modelo(p):
    q = dict(DEFAULTS); q.update(p or {})
    I = int(q['inicio']); L = int(q['lanzamiento']); F = int(q['fin'])
    anios = list(range(I, F+1))
    # --- mercado y volumen
    mercado_us = q['ventas_globales']*q['ventas_eeuu_2025']/q['ventas_global_2025']
    apl_pa = 365.0/q['intervalo']
    precio_apl = q['precio_25'] + q['precio_75']
    mg_adm = q['peso']*q['dosis']
    pac_mercado = mercado_us/(apl_pa*precio_apl*q['neto_lista'])
    if q['usar_fraccion']: retenido = q['fraccion_directa']
    else: retenido = 1.0/((1+q['rec_disp'])*(1+q['rec_dist'])*(1+q['rec_com']))
    # --- produccion
    masa_lote = q['cosecha']*q['titulo']*q['rec_dsp']/1000.0
    masa_final = masa_lote*q['rec_llenado']
    capacidad = _fl(q['dias_disp']/(q['dias_lote']+q['dias_prep']))
    viales_por_lote = 2*_fl(masa_final*1e6/100.0)
    sueldo_anual = q['sueldo']*q['meses']*(1+q['cargas'])
    # --- cronograma de desarrollo (relativo al inicio, como la hoja Desarrollo)
    pers = {0: q['pers_des'], 1: q['pers_bio'], 2: q['pers_bio']}
    lotes_dev = {2: 2, 3: 3, 4: 1}
    dev = {0: q['d_linea']*0.8 + q['d_proceso']*0.2,
           1: q['d_linea']*0.2 + q['d_proceso']*0.4 + q['d_biosim']*0.5,
           2: q['d_proceso']*0.4 + q['d_biosim']*0.5 + q['d_ff']*0.5,
           3: q['d_valid']/3 + q['d_ff']*0.5,
           4: q['d_valid']/3 + q['d_regul']*0.5,
           5: q['d_valid']/3 + q['d_regul']*0.5}
    completo = str(q['programa_clinico']) == 'completo'
    clin_total = q['clinica_completa'] if completo else q['clinica_abreviada']
    ci = int(q['inicio_clinica']) - I; na = max(1, int(round(q['anios_clinica'])))
    clin = {ci + i: clin_total/na for i in range(na)}
    try: rampa = [float(x)/100.0 for x in str(q.get('rampa_cuotas') or '').replace(';', ',').split(',') if x.strip()]
    except ValueError: rampa = []
    cuota_pleno = rampa[-1] if rampa else q['cuota']
    filas = []; prev_ct = 0.0; acum = 0.0; acum_d = 0.0; perdidas = []; flujos = []
    max_lotes = 0
    for y in anios:
        k = y - I
        n = pers.get(k, q['pers_gmp'])
        if y >= L:
            j = y - L
            if rampa: cuota = rampa[min(j, len(rampa)-1)]
            elif q['anios_rampa'] and q['anios_rampa'] > 0 and j < q['anios_rampa']:
                cuota = q['cuota_inicial'] + (q['cuota']-q['cuota_inicial'])*j/q['anios_rampa']
            else: cuota = q['cuota']
            precio_rel = q['precio_rel']*(1-q['caida_precio'])**j
            apl = pac_mercado*cuota*apl_pa
            kg = apl*100.0/1e6
            lotes = _ce(kg*(1+q['reserva'])/masa_final)
            ingreso = apl*precio_apl*precio_rel*retenido
            max_lotes = max(max_lotes, lotes)
        else:
            cuota = 0.0; precio_rel = 0.0; apl = 0.0; lotes = lotes_dev.get(k, 0); ingreso = 0.0
        viales = 2*_fl(lotes*masa_final*1e6/100.0)
        campanas = 2*_ce((viales/2)/q['viales_campana']) if viales else 0
        c_mat = lotes*q['mat_lote']; c_pers = n*sueldo_anual; c_planta = q['op_planta']*n/q['pers_gmp']; c_ens = lotes*q['ensayos_lote']
        c_ffv = viales*q['ff_vial']; c_fff = campanas*q['ff_campana']; c_log = ingreso*q['logistica']
        oper = c_mat + c_pers + c_planta + c_ens + c_ffv + c_fff + c_log
        desarrollo = dev.get(k, 0.0); clinica = clin.get(k, 0.0)
        res = ingreso - oper - desarrollo - clinica
        if res < 0:
            imp = 0.0; perdidas.append([y, -res])
        else:
            base = res
            if q['quebrantos'] and q['quebrantos'] > 0:
                for pr in perdidas:
                    if y - pr[0] <= q['quebrantos'] and base > 0:
                        u = min(pr[1], base); pr[1] -= u; base -= u
            imp = base*q['impuesto']
        ct = oper*q['ct_dias']/365.0 if y >= L else 0.0
        dct = ct - prev_ct; prev_ct = ct
        flujo = res - imp - dct
        fd = flujo/(1+q['tasa'])**k
        acum += flujo; acum_d += fd; flujos.append(flujo)
        filas.append(dict(anio=y, personas=n, lotes=lotes, viales=viales, cuota=cuota, precio_rel=precio_rel,
                          ingresos=ingreso, materiales=c_mat, personal=c_pers, planta=c_planta, ensayos=c_ens,
                          ff_variable=c_ffv, ff_fijo=c_fff, logistica=c_log, operacion=oper, desarrollo=desarrollo, clinica=clinica,
                          resultado=res, impuesto=imp, var_ct=dct, flujo=flujo, acumulado=acum,
                          descontado=fd, acum_descontado=acum_d))
    van = sum(f['descontado'] for f in filas)
    tir = _irr(flujos)
    rec_n = next((f['anio'] for f in filas if f['acumulado'] >= 0), None)
    rec_d = next((f['anio'] for f in filas if f['acum_descontado'] >= 0), None)
    avisos = []
    if max_lotes > capacidad: avisos.append(f"Los lotes anuales ({max_lotes}) superan la capacidad del reactor ({capacidad}).")
    if mg_adm > 100: avisos.append(f"La dosis ({mg_adm:.1f} mg) supera los 100 mg de 1 vial de 75 + 1 de 25; el modelo de viales no aplica.")
    if ci < 4: avisos.append("La clínica empieza antes de tener el lote clínico llenado, liberado y con IND (fin del año 4 desde el inicio).")
    if L < ci + I + na + 1: avisos.append("El lanzamiento es anterior al fin de la clínica más un año de revisión de la FDA.")
    precio_vial = precio_apl*q['precio_rel']/2
    return dict(
        van=van, tir=tir, fondos_max=max(0.0, -min(f['acumulado'] for f in filas)),
        saldo_final=filas[-1]['acumulado'], recupero_nominal=rec_n, recupero_descontado=rec_d,
        mercado_us=mercado_us, pacientes_objetivo=pac_mercado*cuota_pleno, cuota_pleno=cuota_pleno, retenido=retenido,
        ingreso_vial=precio_vial*retenido, precio_vial_biosimilar=precio_vial,
        lotes_max=max_lotes, capacidad=capacidad, masa_final_lote=masa_final,
        programa_clinico='completo' if completo else 'abreviado', clinica_total=clin_total, anios_clinica=na,
        filas=filas, avisos=avisos)

def correr(params_json):
    return json.dumps(modelo(json.loads(params_json)))


if __name__ == "__main__":
    for nombre, cambios in [("70 % · completo", {}), ("60 % · completo", {"precio_rel": 0.60}),
                            ("70 % · abreviado", {"programa_clinico": "abreviado"}),
                            ("60 % · abreviado", {"precio_rel": 0.60, "programa_clinico": "abreviado"})]:
        r = modelo(cambios)
        tir = "sin TIR" if r["tir"] is None else f"{r['tir']*100:.2f} %"
        print(f"{nombre:17s} VAN = {r['van']/1e6:8.2f} M USD   TIR = {tir:>8s}   "
              f"fondos máx. = {r['fondos_max']/1e6:7.2f} M   recupero = {r['recupero_nominal']}/{r['recupero_descontado']}")
