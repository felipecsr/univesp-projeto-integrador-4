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
  const configRows = getObjects_(TAB.CONFIG);
  const config = {};
  configRows.forEach(function (row) {
    config[String(row.CHAVE)] = row.VALOR;
  });

  const catalog = getObjects_(TAB.CATALOGO);
  const comparables = getObjects_(TAB.COMPARAVEIS);
  const schools = getObjects_(TAB.ESCOLAS)
    .filter(function (row) {
      return String(row.CO_MUNICIPIO) === String(config.MUNICIPIO_FOCO || '3518404');
    });

  const redes = unique_(schools.map(function (row) { return row.REDE; }).filter(Boolean));
  const zonas = unique_(schools.map(function (row) { return row.ZONA; }).filter(Boolean));

  return {
    config: config,
    catalog: catalog,
    comparables: comparables,
    filters: {
      years: ['2023', '2024', '2025'],
      redes: redes,
      zonas: zonas,
    },
  };
}

function getOverviewData(filters) {
  filters = filters || {};
  const config = config_();
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
    snapshot = aggregateSchools2025_(municipalityCode, rede, zona);
  } else {
    const rows = getObjects_(TAB.MUNICIPIO_ANO).filter(function (row) {
      return String(row.CO_MUNICIPIO) === municipalityCode &&
        String(row.NU_ANO_CENSO) === year;
    });
    if (!rows.length) throw new Error('Recorte municipal não encontrado.');
    snapshot = rowToSnapshot_(rows[0]);
  }

  const history = getObjects_(TAB.MUNICIPIO_ANO)
    .filter(function (row) {
      return String(row.CO_MUNICIPIO) === municipalityCode;
    })
    .sort(function (a, b) {
      return Number(a.NU_ANO_CENSO) - Number(b.NU_ANO_CENSO);
    })
    .map(rowToSnapshot_);

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

function getComparisonData(params) {
  params = params || {};
  const config = config_();
  const indicatorId = String(params.indicatorId || 'internet');
  const year = String(params.year || config.ANO_PADRAO || '2025');
  const mode = String(params.mode || 'schools');

  const comparisonCodes = getObjects_(TAB.COMPARAVEIS)
    .map(function (row) { return String(row.CO_MUNICIPIO); });

  const rows = getObjects_(TAB.MUNICIPIO_ANO)
    .filter(function (row) {
      return String(row.NU_ANO_CENSO) === year &&
        comparisonCodes.indexOf(String(row.CO_MUNICIPIO)) >= 0;
    });

  const pctKey = (mode === 'enrollments' ? 'PCTPOND_' : 'PCT_') + indicatorId;
  const validKey = (mode === 'enrollments' ? 'N_VALIDOS_POND_' : 'N_VALIDOS_') + indicatorId;
  const focusCode = String(config.MUNICIPIO_FOCO || '3518404');

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

  return {
    indicatorId: indicatorId,
    year: year,
    mode: mode,
    rows: output,
  };
}

function searchSchools(params) {
  params = params || {};
  const config = config_();
  const municipalityCode = String(config.MUNICIPIO_FOCO || '3518404');
  const query = normalizeText_(String(params.query || ''));
  const rede = String(params.rede || '');
  const zona = String(params.zona || '');

  return getObjects_(TAB.ESCOLAS)
    .filter(function (row) {
      if (String(row.CO_MUNICIPIO) !== municipalityCode) return false;
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

  const school = getObjects_(TAB.ESCOLAS).find(function (row) {
    return String(row.CO_ENTIDADE) === codeText &&
      String(row.CO_MUNICIPIO) === municipalityCode;
  });

  if (!school) throw new Error('Escola não encontrada.');

  const municipality = getObjects_(TAB.MUNICIPIO_ANO).find(function (row) {
    return String(row.CO_MUNICIPIO) === municipalityCode &&
      String(row.NU_ANO_CENSO) === '2025';
  });

  const catalog = getObjects_(TAB.CATALOGO)
    .filter(function (row) { return String(row.TIPO) === 'Percentual'; });

  const indicators = catalog.map(function (item) {
    const source = String(item.VARIAVEL_FONTE);
    const id = String(item.ID);
    return {
      id: id,
      label: item.INDICADOR,
      dimension: item.DIMENSAO,
      schoolValue: numericOrNull_(school[source]),
      municipalityValue: municipality ? numericOrNull_(municipality['PCT_' + id]) : null,
      validMunicipality: municipality ? numericOrNull_(municipality['N_VALIDOS_' + id]) : null,
    };
  });

  return {
    code: String(school.CO_ENTIDADE),
    name: school.NO_ENTIDADE,
    rede: school.REDE,
    zona: school.ZONA,
    rooms: numericOrNull_(school.QT_SALAS_UTILIZADAS),
    enrollments: numericOrNull_(school.QT_MAT_BAS),
    indicators: indicators,
  };
}

function getMethodologyData() {
  return {
    config: getObjects_(TAB.CONFIG),
    catalog: getObjects_(TAB.CATALOGO),
    comparables: getObjects_(TAB.COMPARAVEIS),
  };
}

function aggregateSchools2025_(municipalityCode, rede, zona) {
  const rows = getObjects_(TAB.ESCOLAS).filter(function (row) {
    if (String(row.CO_MUNICIPIO) !== municipalityCode) return false;
    if (rede && String(row.REDE) !== rede) return false;
    if (zona && String(row.ZONA) !== zona) return false;
    return true;
  });

  const catalog = getObjects_(TAB.CATALOGO)
    .filter(function (row) { return String(row.TIPO) === 'Percentual'; });

  const snapshot = {
    year: '2025',
    municipalityCode: municipalityCode,
    municipality: rows.length ? rows[0].NO_MUNICIPIO : '',
    schools: unique_(rows.map(function (row) { return String(row.CO_ENTIDADE); })).length,
    enrollments: sumNullable_(rows.map(function (row) { return row.QT_MAT_BAS; })),
    rooms: sumNullable_(rows.map(function (row) { return row.QT_SALAS_UTILIZADAS; })),
    indicators: {},
  };

  catalog.forEach(function (item) {
    const source = String(item.VARIAVEL_FONTE);
    const id = String(item.ID);
    const valid = rows.filter(function (row) { return isNumberLike_(row[source]); });
    const simple = valid.length
      ? valid.reduce(function (acc, row) { return acc + Number(row[source]); }, 0) / valid.length
      : null;

    const weightedRows = valid.filter(function (row) {
      return isNumberLike_(row.QT_MAT_BAS);
    });
    const denominator = weightedRows.reduce(function (acc, row) {
      return acc + Number(row.QT_MAT_BAS);
    }, 0);
    const weighted = denominator > 0
      ? weightedRows.reduce(function (acc, row) {
          return acc + Number(row[source]) * Number(row.QT_MAT_BAS);
        }, 0) / denominator
      : null;

    snapshot.indicators[id] = {
      simple: simple,
      weighted: weighted,
      valid: valid.length,
      weightedValid: weightedRows.length,
      baseSmall: valid.length < Number(config_().BASE_PEQUENA_LIMITE || 5),
    };
  });

  return snapshot;
}

function rowToSnapshot_(row) {
  const catalog = getObjects_(TAB.CATALOGO)
    .filter(function (item) { return String(item.TIPO) === 'Percentual'; });
  const indicators = {};

  catalog.forEach(function (item) {
    const id = String(item.ID);
    indicators[id] = {
      simple: numericOrNull_(row['PCT_' + id]),
      weighted: numericOrNull_(row['PCTPOND_' + id]),
      valid: numericOrNull_(row['N_VALIDOS_' + id]),
      weightedValid: numericOrNull_(row['N_VALIDOS_POND_' + id]),
      baseSmall: numericOrNull_(row['N_VALIDOS_' + id]) !== null &&
        numericOrNull_(row['N_VALIDOS_' + id]) < Number(config_().BASE_PEQUENA_LIMITE || 5),
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
  const rows = getObjects_(TAB.CONFIG);
  const config = {};
  rows.forEach(function (row) {
    config[String(row.CHAVE)] = row.VALOR;
  });
  return config;
}

function getObjects_(sheetName) {
  const cache = CacheService.getScriptCache();
  const cacheKey = 'tab:' + sheetName;
  const cached = cache.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const sheet = SpreadsheetApp.openById(DATA_SPREADSHEET_ID).getSheetByName(sheetName);
  if (!sheet) throw new Error('Aba não encontrada: ' + sheetName);

  const values = sheet.getDataRange().getValues();
  if (!values.length) return [];
  const headers = values.shift().map(String);

  const objects = values
    .filter(function (row) {
      return row.some(function (value) { return value !== '' && value !== null; });
    })
    .map(function (row) {
      const obj = {};
      headers.forEach(function (header, index) {
        obj[header] = row[index];
      });
      return obj;
    });

  try {
    cache.put(cacheKey, JSON.stringify(objects), 300);
  } catch (err) {
    // Tabelas grandes podem exceder o limite do cache; a leitura direta permanece válida.
  }
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
  const numeric = values
    .map(numericOrNull_)
    .filter(function (value) { return value !== null; });
  if (!numeric.length) return null;
  return numeric.reduce(function (acc, value) { return acc + value; }, 0);
}

function normalizeText_(value) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();
}
