/**
 * Sidebar and configuration helpers for the A+ Workspace setup project.
 *
 * Existing provisioning helpers (setupWorkspace, backfill, ensureLabels_, etc.)
 * should live above this section. These utilities only append new behavior.
 */

function onOpen(e) {
  var ui = null;
  if (typeof SpreadsheetApp !== 'undefined' && SpreadsheetApp.getUi) {
    ui = SpreadsheetApp.getUi();
  } else if (typeof DocumentApp !== 'undefined' && DocumentApp.getUi) {
    ui = DocumentApp.getUi();
  } else if (typeof SlidesApp !== 'undefined' && SlidesApp.getUi) {
    ui = SlidesApp.getUi();
  } else if (typeof FormApp !== 'undefined' && FormApp.getUi) {
    ui = FormApp.getUi();
  }

  if (ui) {
    ui.createMenu('A+ Workspace')
      .addItem('Open Setup Sidebar', 'showSidebar')
      .addToUi();
  }
}

function showSidebar() {
  var sidebar = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('A+ Workspace Setup')
    .setWidth(360);

  var ui = null;
  if (typeof SpreadsheetApp !== 'undefined' && SpreadsheetApp.getUi) {
    ui = SpreadsheetApp.getUi();
  } else if (typeof DocumentApp !== 'undefined' && DocumentApp.getUi) {
    ui = DocumentApp.getUi();
  } else if (typeof SlidesApp !== 'undefined' && SlidesApp.getUi) {
    ui = SlidesApp.getUi();
  } else if (typeof FormApp !== 'undefined' && FormApp.getUi) {
    ui = FormApp.getUi();
  }

  if (ui && ui.showSidebar) {
    ui.showSidebar(sidebar);
  } else {
    throw new Error('Sidebar UI is not available in this script context.');
  }
}

function getConfig() {
  var stored = _readConfigFromProps_();
  var fallback = stored;

  if (!fallback) {
    if (typeof CONFIG !== 'undefined') {
      try {
        if (typeof CONFIG === 'string') {
          fallback = JSON.parse(CONFIG);
        } else {
          fallback = CONFIG;
        }
      } catch (err) {
        Logger.log('Failed to parse CONFIG fallback: ' + err);
        fallback = {};
      }
    } else {
      fallback = {};
    }
  }

  var sanitized = sanitizeConfig_(fallback || {});
  return JSON.parse(JSON.stringify(sanitized));
}

function setConfig(json) {
  var parsed;
  if (json === null || json === undefined) {
    parsed = {};
  } else if (typeof json === 'string') {
    try {
      parsed = JSON.parse(json);
    } catch (err) {
      throw new Error('Invalid JSON: ' + err.message);
    }
  } else if (typeof json === 'object') {
    parsed = json;
  } else {
    throw new Error('Unsupported config payload. Provide JSON data.');
  }

  var sanitized = sanitizeConfig_(parsed);
  _writeConfigToProps_(sanitized);
  return JSON.parse(JSON.stringify(sanitized));
}

function runAction(name, args) {
  if (!name) {
    throw new Error('Action name is required.');
  }

  var action = String(name);
  var payload = args || {};

  if (action === 'setup') {
    setupWorkspace();
  } else if (action === 'backfill') {
    var days = Number(payload.days);
    if (isNaN(days) || days <= 0) {
      days = 14;
    }
    backfill(days);
  } else if (action === 'dailyTrigger') {
    createDailyBackfillTrigger();
  } else if (action === 'deleteTriggers') {
    deleteAllTriggers();
  } else {
    throw new Error('Unknown action: ' + action);
  }

  return { ok: true };
}

function _readConfigFromProps_() {
  var props = PropertiesService.getScriptProperties();
  var raw = props.getProperty('CONFIG');
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch (err) {
    Logger.log('Unable to parse stored CONFIG: ' + err);
    return null;
  }
}

function _writeConfigToProps_(obj) {
  var props = PropertiesService.getScriptProperties();
  if (!obj || (typeof obj === 'object' && Object.keys(obj).length === 0)) {
    props.deleteProperty('CONFIG');
    return;
  }
  props.setProperty('CONFIG', JSON.stringify(obj));
}

function sanitizeConfig_(obj) {
  var source;
  if (obj && typeof obj === 'object') {
    try {
      source = JSON.parse(JSON.stringify(obj));
    } catch (err) {
      Logger.log('Failed to clone config, using shallow copy. ' + err);
      source = obj;
    }
  } else {
    source = {};
  }

  if (!Array.isArray(source.vipContacts)) {
    source.vipContacts = [];
  }

  if (!Array.isArray(source.vipDomains)) {
    source.vipDomains = [];
  }

  if (typeof source.labels === 'undefined' || source.labels === null) {
    source.labels = [];
  }

  if (!source.drive || typeof source.drive !== 'object') {
    source.drive = {};
  }
  if (!source.drive.root || typeof source.drive.root !== 'string') {
    source.drive.root = 'A+ Workspace';
  }
  if (!Array.isArray(source.drive.subfolders)) {
    source.drive.subfolders = [];
  }

  if (!Array.isArray(source.calendars)) {
    source.calendars = [];
  }

  if (!Array.isArray(source.filters)) {
    source.filters = [];
  }

  return source;
}
