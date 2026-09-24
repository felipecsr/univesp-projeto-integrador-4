const DATA_SPREADSHEET_ID = '1qrutI54-srUXcr-tcwjy23W99v1_KNFAF5kfRlBuxMA';

const TAB = {
  CONFIG: 'CONFIG',
  CATALOGO: 'CATALOGO',
  COMPARAVEIS: 'COMPARAVEIS',
  MUNICIPIO_ANO: 'MUNICIPIO_ANO',
  MUNICIPIO_REDE: 'MUNICIPIO_REDE_2025',
  MUNICIPIO_ZONA: 'MUNICIPIO_ZONA_2025',
  ESCOLAS: 'ESCOLAS_2025',
};

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Infraestrutura Escolar — Guaratinguetá')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getBootstrapData() {
  const config = config_();
  const catalog = catalog_();
  const comparables = getObjects_(TAB.COMPARAVEIS);
  const municipalityCode = String(config.MUNICIPIO_FOCO || '3518404');
  const schools = getRowsByValue_(TAB.ESCOLAS, 'CO_MUNICIPIO', municipalityCode);
  const municipalityRows = getRowsByValue_(TAB.MUNICIPIO_ANO, 'CO_MUNICIPIO', municipalityCode);
  const defaultYear = String(config.ANO_PADRAO || '2025');
  const defaultRow = municipalityRows.find(function (row) { return String(row.NU_ANO_CENSO) === defaultYear; });
  const initialOverview = defaultRow ? {
    municipalityCode: municipalityCode,
    year: defaultYear,
    mode: 'schools',
    rede: '',
    zona: '',
    snapshot: rowToSnapshot_(defaultRow, catalog, config),
    history: municipalityRows.sort(function (a, b) { return Number(a.NU_ANO_CENSO) - Number(b.NU_ANO_CENSO); })
      .map(function (row) { return rowToSnapshot_(row, catalog, config); }),
  } : null;

  return {
    config: config,
    catalog: catalog,
    comparables: comparables,
    initialOverview: initialOverview,
    filters: {
      years: ['2023', '2024', '2025'],
      redes: unique_(schools.map(function (row) { return row.REDE; }).filter(Boolean)),
      zonas: unique_(schools.map(function (row) { return row.ZONA; }).filter(Boolean)),
    },
  };
}

function getOverviewData(filters) {
  filters = filters || {};
  const config = config_();
  const catalog = catalog_();
  const municipalityCode = String(filters.municipalityCode || config.MUNICIPIO_FOCO || '3518404');
  const year = String(filters.year || config.ANO_PADRAO || '2025');
  const mode = String(filters.mode || 'schools');
  const rede = String(filters.rede || '');
  const zona = String(filters.zona || '');

  if (year !== '2025' && (rede || zona)) {
    throw new Error('Os filtros de rede e zona estão disponíveis somente para a fotografia de 2025 no MVP.');
  }

  let snapshot;
  if (year === '2025' && (rede || zona)) {
    snapshot = aggregateFocusSchools2025_(municipalityCode, rede, zona, catalog, config);
  } else {
    const rows = getRowsByValue_(TAB.MUNICIPIO_ANO, 'CO_MUNICIPIO', municipalityCode);
    const row = rows.find(function (item) { return String(item.NU_ANO_CENSO) === year; });
    if (!row) throw new Error('Recorte municipal não encontrado.');
    snapshot = rowToSnapshot_(row, catalog, config);
  }

  const history = getRowsByValue_(TAB.MUNICIPIO_ANO, 'CO_MUNICIPIO', municipalityCode)
    .sort(function (a, b) { return Number(a.NU_ANO_CENSO) - Number(b.NU_ANO_CENSO); })
    .map(function (row) { return rowToSnapshot_(row, catalog, config); });

  return {
    municipalityCode: municipalityCode,
    year: year,
    mode: mode,
    rede: rede,
    zona: zona,
    snapshot: snapshot,
    history: history,
  };
}

function getBreakdownData(params) {
  params = params || {};
  const config = config_();
  const municipalityCode = String(config.MUNICIPIO_FOCO || '3518404');
  const indicatorId = String(params.indicatorId || 'internet');
  const mode = String(params.mode || 'schools');
  const valueKey = (mode === 'enrollments' ? 'PCTPOND_' : 'PCT_') + indicatorId;
  const validKey = (mode === 'enrollments' ? 'N_VALIDOS_POND_' : 'N_VALIDOS_') + indicatorId;

  const networkRows = getRowsByValue_(TAB.MUNICIPIO_REDE, 'CO_MUNICIPIO', municipalityCode);
  const zoneRows = getRowsByValue_(TAB.MUNICIPIO_ZONA, 'CO_MUNICIPIO', municipalityCode);

  return {
    indicatorId: indicatorId,
    mode: mode,
    networks: networkRows.map(function (row) {
      return {
        label: row.REDE,
        value: numericOrNull_(row[valueKey]),
        valid: numericOrNull_(row[validKey]),
        schools: numericOrNull_(row.N_ESCOLAS),
        baseSmall: numericOrNull_(row.N_ESCOLAS) !== null && numericOrNull_(row.N_ESCOLAS) < Number(config.BASE_PEQUENA_LIMITE || 5),
      };
    }),
    zones: zoneRows.map(function (row) {
      return {
        label: row.ZONA,
        value: numericOrNull_(row[valueKey]),
        valid: numericOrNull_(row[validKey]),
        schools: numericOrNull_(row.N_ESCOLAS),
        baseSmall: Boolean(row.BASE_PEQUENA),
      };
    }),
  };
}

function getComparisonData(params) {
  params = params || {};
  const config = config_();
  const indicatorId = String(params.indicatorId || 'internet');
  const year = String(params.year || config.ANO_PADRAO || '2025');
  const mode = String(params.mode || 'schools');
  const comparisonCodes = getObjects_(TAB.COMPARAVEIS).map(function (row) { return String(row.CO_MUNICIPIO); });
  const pctKey = (mode === 'enrollments' ? 'PCTPOND_' : 'PCT_') + indicatorId;
  const validKey = (mode === 'enrollments' ? 'N_VALIDOS_POND_' : 'N_VALIDOS_') + indicatorId;
  const focusCode = String(config.MUNICIPIO_FOCO || '3518404');

  const rows = getObjects_(TAB.MUNICIPIO_ANO).filter(function (row) {
    return String(row.NU_ANO_CENSO) === year && comparisonCodes.indexOf(String(row.CO_MUNICIPIO)) >= 0;
  });

  const output = rows.map(function (row) {
    return {
      municipalityCode: String(row.CO_MUNICIPIO),
      municipality: row.NO_MUNICIPIO,
      value: numericOrNull_(row[pctKey]),
      valid: numericOrNull_(row[validKey]),
      schools: numericOrNull_(row.N_ESCOLAS),
      enrollments: numericOrNull_(row.QT_MAT_BAS),
      focus: String(row.CO_MUNICIPIO) === focusCode,
    };
  });

  output.sort(function (a, b) {
    if (a.value === null && b.value === null) return 0;
    if (a.value === null) return 1;
    if (b.value === null) return -1;
    return b.value - a.value;
  });

  return { indicatorId: indicatorId, year: year, mode: mode, rows: output };
}

function getComparableProfileData(params) {
  params = params || {};
  const config = config_();
  const year = String(params.year || config.ANO_PADRAO || '2025');
  const mode = String(params.mode || 'schools');
  const focusCode = String(config.MUNICIPIO_FOCO || '3518404');
  const codes = getObjects_(TAB.COMPARAVEIS).map(function (row) { return String(row.CO_MUNICIPIO); });
  const rows = getObjects_(TAB.MUNICIPIO_ANO).filter(function (row) {
    return String(row.NU_ANO_CENSO) === year && codes.indexOf(String(row.CO_MUNICIPIO)) >= 0;
  });
  const focus = rows.find(function (row) { return String(row.CO_MUNICIPIO) === focusCode; });
  const others = rows.filter(function (row) { return String(row.CO_MUNICIPIO) !== focusCode; });
  const catalog = catalog_().filter(function (row) { return String(row.TIPO) === 'Percentual'; });

  return {
    year: year,
    mode: mode,
    rows: catalog.map(function (item) {
      const id = String(item.ID);
      const key = (mode === 'enrollments' ? 'PCTPOND_' : 'PCT_') + id;
      const vals = others.map(function (row) { return numericOrNull_(row[key]); }).filter(function (v) { return v !== null; });
      return {
        id: id,
        label: item.INDICADOR,
        focus: focus ? numericOrNull_(focus[key]) : null,
        comparableMean: vals.length ? vals.reduce(function (a, v) { return a + v; }, 0) / vals.length : null,
      };
    }),
  };
}

function getComparisonBundle(params) {
  params = params || {};
  const config = config_();
  const mode = String(params.mode || 'schools');
  const indicatorId = String(params.indicatorId || 'internet');
  const focusCode = String(config.MUNICIPIO_FOCO || '3518404');
  const requestedYears = Array.isArray(params.years) && params.years.length
    ? params.years.map(String)
    : ['2023', '2024', '2025'];
  const years = ['2023', '2024', '2025'].filter(function (year) {
    return requestedYears.indexOf(year) >= 0;
  });
  const codes = getObjects_(TAB.COMPARAVEIS).map(function (row) { return String(row.CO_MUNICIPIO); });
  const allRows = getObjects_(TAB.MUNICIPIO_ANO).filter(function (row) {
    return years.indexOf(String(row.NU_ANO_CENSO)) >= 0 &&
      codes.indexOf(String(row.CO_MUNICIPIO)) >= 0;
  });
  const pctPrefix = mode === 'enrollments' ? 'PCTPOND_' : 'PCT_';
  const validPrefix = mode === 'enrollments' ? 'N_VALIDOS_POND_' : 'N_VALIDOS_';
  const valueKey = pctPrefix + indicatorId;
  const validKey = validPrefix + indicatorId;

  const municipalityMap = {};
  allRows.forEach(function (row) {
    const code = String(row.CO_MUNICIPIO);
    if (!municipalityMap[code]) {
      municipalityMap[code] = {
        municipalityCode: code,
        municipality: row.NO_MUNICIPIO,
        focus: code === focusCode,
        byYear: {},
      };
    }
    municipalityMap[code].byYear[String(row.NU_ANO_CENSO)] = {
      value: numericOrNull_(row[valueKey]),
      valid: numericOrNull_(row[validKey]),
      schools: numericOrNull_(row.N_ESCOLAS),
      enrollments: numericOrNull_(row.QT_MAT_BAS),
    };
  });

  const municipalities = codes.map(function (code) { return municipalityMap[code]; })
    .filter(Boolean);

  const latestYear = years.length ? years[years.length - 1] : '2025';
  municipalities.sort(function (a, b) {
    const av = a.byYear[latestYear] ? a.byYear[latestYear].value : null;
    const bv = b.byYear[latestYear] ? b.byYear[latestYear].value : null;
    if (av === null && bv === null) return 0;
    if (av === null) return 1;
    if (bv === null) return -1;
    return bv - av;
  });

  const catalog = catalog_().filter(function (row) { return String(row.TIPO) === 'Percentual'; });
  const profileRows = catalog.map(function (item) {
    const id = String(item.ID);
    const key = pctPrefix + id;
    const focusValues = allRows
      .filter(function (row) { return String(row.CO_MUNICIPIO) === focusCode; })
      .map(function (row) { return numericOrNull_(row[key]); })
      .filter(function (v) { return v !== null; });
    const comparableValues = allRows
      .filter(function (row) { return String(row.CO_MUNICIPIO) !== focusCode; })
      .map(function (row) { return numericOrNull_(row[key]); })
      .filter(function (v) { return v !== null; });

    return {
      id: id,
      label: item.INDICADOR,
      focus: meanNullable_(focusValues),
      comparableMean: meanNullable_(comparableValues),
    };
  });

  const scatter = municipalities.map(function (item) {
    const point = item.byYear[latestYear] || {};
    return {
      municipalityCode: item.municipalityCode,
      municipality: item.municipality,
      focus: item.focus,
      year: latestYear,
      value: point.value == null ? null : point.value,
      enrollments: point.enrollments == null ? null : point.enrollments,
      schools: point.schools == null ? null : point.schools,
    };
  }).filter(function (row) {
    return row.value !== null && row.enrollments !== null && row.schools !== null;
  });

  return {
    comparison: {
      indicatorId: indicatorId,
      years: years,
      latestYear: latestYear,
      mode: mode,
      municipalities: municipalities,
    },
    profile: {
      years: years,
      mode: mode,
      rows: profileRows,
    },
    scatter: scatter,
  };
}

function searchSchools(params) {
  params = params || {};
  const config = config_();
  const municipalityCode = String(config.MUNICIPIO_FOCO || '3518404');
  const query = normalizeText_(String(params.query || ''));
  const rede = String(params.rede || '');
  const zona = String(params.zona || '');

  return getRowsByValue_(TAB.ESCOLAS, 'CO_MUNICIPIO', municipalityCode)
    .filter(function (row) {
      if (rede && String(row.REDE) !== rede) return false;
      if (zona && String(row.ZONA) !== zona) return false;
      if (query && normalizeText_(String(row.NO_ENTIDADE)).indexOf(query) < 0) return false;
      return true;
    })
    .slice(0, 100)
    .map(function (row) {
      return {
        code: String(row.CO_ENTIDADE),
        name: row.NO_ENTIDADE,
        rede: row.REDE,
        zona: row.ZONA,
        enrollments: numericOrNull_(row.QT_MAT_BAS),
      };
    });
}

function getSchoolDetail(code) {
  const config = config_();
  const municipalityCode = String(config.MUNICIPIO_FOCO || '3518404');
  const codeText = String(code);
  const school = getRowsByValue_(TAB.ESCOLAS, 'CO_MUNICIPIO', municipalityCode).find(function (row) {
    return String(row.CO_ENTIDADE) === codeText;
  });
  if (!school) throw new Error('Escola não encontrada.');

  const municipalityRows = getRowsByValue_(TAB.MUNICIPIO_ANO, 'CO_MUNICIPIO', municipalityCode);
  const municipality = municipalityRows.find(function (row) {
    return String(row.NU_ANO_CENSO) === '2025';
  });
  const comparableCodes = getObjects_(TAB.COMPARAVEIS)
    .map(function (row) { return String(row.CO_MUNICIPIO); })
    .filter(function (code) { return code !== municipalityCode; });
  const comparable2025 = getObjects_(TAB.MUNICIPIO_ANO).filter(function (row) {
    return String(row.NU_ANO_CENSO) === '2025' &&
      comparableCodes.indexOf(String(row.CO_MUNICIPIO)) >= 0;
  });
  const catalog = catalog_().filter(function (row) { return String(row.TIPO) === 'Percentual'; });

  return {
    code: String(school.CO_ENTIDADE),
    name: school.NO_ENTIDADE,
    rede: school.REDE,
    zona: school.ZONA,
    rooms: numericOrNull_(school.QT_SALAS_UTILIZADAS),
    enrollments: numericOrNull_(school.QT_MAT_BAS),
    indicators: catalog.map(function (item) {
      const source = String(item.VARIAVEL_FONTE);
      const id = String(item.ID);
      const comparableValues = comparable2025
        .map(function (row) { return numericOrNull_(row['PCT_' + id]); })
        .filter(function (v) { return v !== null; });
      return {
        id: id,
        label: item.INDICADOR,
        dimension: item.DIMENSAO,
        schoolValue: numericOrNull_(school[source]),
        municipalityValue: municipality ? numericOrNull_(municipality['PCT_' + id]) : null,
        comparableMean: meanNullable_(comparableValues),
        validMunicipality: municipality ? numericOrNull_(municipality['N_VALIDOS_' + id]) : null,
      };
    }),
  };
}

function getMethodologyData() {
  return {
    config: getObjects_(TAB.CONFIG),
    catalog: catalog_(),
    comparables: getObjects_(TAB.COMPARAVEIS),
  };
}

function aggregateFocusSchools2025_(municipalityCode, rede, zona, catalog, config) {
  const rows = getRowsByValue_(TAB.ESCOLAS, 'CO_MUNICIPIO', municipalityCode).filter(function (row) {
    if (rede && String(row.REDE) !== rede) return false;
    if (zona && String(row.ZONA) !== zona) return false;
    return true;
  });

  const snapshot = {
    year: '2025',
    municipalityCode: municipalityCode,
    municipality: rows.length ? rows[0].NO_MUNICIPIO : '',
    schools: unique_(rows.map(function (row) { return String(row.CO_ENTIDADE); })).length,
    enrollments: sumNullable_(rows.map(function (row) { return row.QT_MAT_BAS; })),
    rooms: sumNullable_(rows.map(function (row) { return row.QT_SALAS_UTILIZADAS; })),
    indicators: {},
  };

  catalog.filter(function (item) { return String(item.TIPO) === 'Percentual'; }).forEach(function (item) {
    const source = String(item.VARIAVEL_FONTE);
    const id = String(item.ID);
    const valid = rows.filter(function (row) { return isNumberLike_(row[source]); });
    const simple = valid.length ? valid.reduce(function (acc, row) { return acc + Number(row[source]); }, 0) / valid.length : null;
    const weightedRows = valid.filter(function (row) { return isNumberLike_(row.QT_MAT_BAS); });
    const denominator = weightedRows.reduce(function (acc, row) { return acc + Number(row.QT_MAT_BAS); }, 0);
    const weighted = denominator > 0
      ? weightedRows.reduce(function (acc, row) { return acc + Number(row[source]) * Number(row.QT_MAT_BAS); }, 0) / denominator
      : null;

    snapshot.indicators[id] = {
      simple: simple,
      weighted: weighted,
      valid: valid.length,
      weightedValid: weightedRows.length,
      baseSmall: valid.length < Number(config.BASE_PEQUENA_LIMITE || 5),
    };
  });

  return snapshot;
}

function rowToSnapshot_(row, catalog, config) {
  const indicators = {};
  catalog.filter(function (item) { return String(item.TIPO) === 'Percentual'; }).forEach(function (item) {
    const id = String(item.ID);
    const valid = numericOrNull_(row['N_VALIDOS_' + id]);
    indicators[id] = {
      simple: numericOrNull_(row['PCT_' + id]),
      weighted: numericOrNull_(row['PCTPOND_' + id]),
      valid: valid,
      weightedValid: numericOrNull_(row['N_VALIDOS_POND_' + id]),
      baseSmall: valid !== null && valid < Number(config.BASE_PEQUENA_LIMITE || 5),
    };
  });

  return {
    year: String(row.NU_ANO_CENSO),
    municipalityCode: String(row.CO_MUNICIPIO),
    municipality: row.NO_MUNICIPIO,
    schools: numericOrNull_(row.N_ESCOLAS),
    enrollments: numericOrNull_(row.QT_MAT_BAS),
    rooms: numericOrNull_(row.QT_SALAS_UTILIZADAS),
    indicators: indicators,
  };
}

function config_() {
  const config = {};
  getObjects_(TAB.CONFIG).forEach(function (row) { config[String(row.CHAVE)] = row.VALOR; });
  return config;
}

function catalog_() {
  return getObjects_(TAB.CATALOGO);
}

function getRowsByValue_(sheetName, keyColumn, keyValue) {
  const cache = CacheService.getScriptCache();
  const cacheKey = 'focus:v2:' + sheetName + ':' + keyColumn + ':' + keyValue;
  const cached = cache.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const sheet = SpreadsheetApp.openById(DATA_SPREADSHEET_ID).getSheetByName(sheetName);
  if (!sheet) throw new Error('Aba não encontrada: ' + sheetName);
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow < 2 || lastCol < 1) return [];

  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
  const keyIndex = headers.indexOf(keyColumn);
  if (keyIndex < 0) throw new Error('Coluna não encontrada em ' + sheetName + ': ' + keyColumn);

  const keys = sheet.getRange(2, keyIndex + 1, lastRow - 1, 1).getValues();
  let first = -1;
  let last = -1;
  for (let i = 0; i < keys.length; i++) {
    if (String(keys[i][0]) === String(keyValue)) {
      if (first < 0) first = i + 2;
      last = i + 2;
    }
  }
  if (first < 0) return [];

  const values = sheet.getRange(first, 1, last - first + 1, lastCol).getValues();
  const rows = values.map(function (row) {
    const obj = {};
    headers.forEach(function (header, index) { obj[header] = row[index]; });
    return obj;
  }).filter(function (row) { return String(row[keyColumn]) === String(keyValue); });

  try { cache.put(cacheKey, JSON.stringify(rows), 1800); } catch (err) {}
  return rows;
}

function getObjects_(sheetName) {
  const cache = CacheService.getScriptCache();
  const cacheKey = 'tab:v2:' + sheetName;
  const cached = cache.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const sheet = SpreadsheetApp.openById(DATA_SPREADSHEET_ID).getSheetByName(sheetName);
  if (!sheet) throw new Error('Aba não encontrada: ' + sheetName);
  const values = sheet.getDataRange().getValues();
  if (!values.length) return [];
  const headers = values.shift().map(String);
  const objects = values.filter(function (row) {
    return row.some(function (value) { return value !== '' && value !== null; });
  }).map(function (row) {
    const obj = {};
    headers.forEach(function (header, index) { obj[header] = row[index]; });
    return obj;
  });

  try { cache.put(cacheKey, JSON.stringify(objects), 900); } catch (err) {}
  return objects;
}

function unique_(values) {
  return Array.from(new Set(values)).sort();
}

function numericOrNull_(value) {
  if (value === '' || value === null || typeof value === 'undefined') return null;
  const number = Number(value);
  return isNaN(number) ? null : number;
}

function isNumberLike_(value) {
  return numericOrNull_(value) !== null;
}

function sumNullable_(values) {
  const numeric = values.map(numericOrNull_).filter(function (value) { return value !== null; });
  if (!numeric.length) return null;
  return numeric.reduce(function (acc, value) { return acc + value; }, 0);
}

function meanNullable_(values) {
  const numeric = (values || []).map(numericOrNull_).filter(function (value) { return value !== null; });
  if (!numeric.length) return null;
  return numeric.reduce(function (acc, value) { return acc + value; }, 0) / numeric.length;
}

function normalizeText_(value) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
}