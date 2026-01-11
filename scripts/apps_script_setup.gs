/**
 * Google Apps Script helper to configure Gmail, Drive, and Calendar.
 *
 * Paste this file into script.google.com, enable the Gmail advanced service,
 * and run {@link runAll} (or the individual setup functions) to provision
 * labels, filters, Drive folders, and calendars.
 */

// ---- Configuration: edit these values to fit your workflow. ----

/**
 * VIP contact definitions used to build Gmail filters.
 *
 * Add or remove entries to control which senders receive VIP treatment.
 * Each entry groups one or more email addresses underneath the label that
 * should be applied to the incoming message. All VIP mail is starred and
 * marked as "Never send to spam" automatically.
 */
const VIP_CONTACTS = [
  {
    label: 'VIP/Buyers',
    addresses: [
      // 'client@example.com',
    ],
  },
  {
    label: 'VIP/Family',
    addresses: [
      // 'family.member@example.com',
    ],
  },
];

/**
 * Internal domain used to identify team member mail.
 * Update this value if your organization changes domains.
 */
const INTERNAL_DOMAIN = 'aplus-enterprise.com';

/**
 * Maximum number of threads to inspect per filter when applying labels to
 * existing conversations.
 */
const THREAD_SAMPLING_LIMIT = 2000;

/**
 * Gmail labels that should exist before filters are created.
 */
const REQUIRED_LABELS = [
  'VIP/Buyers',
  'VIP/Family',
  'GovCon/RFP',
  'Sales/Leads',
  'Finance/Invoices',
  'Vendors',
  'School/MSU',
  'Legal/Compliance',
  'Internal/Agents',
  'Newsletters',
];

/**
 * Folder structure created under the "A+ Workspace" root Drive folder.
 */
const DRIVE_SUBFOLDERS = [
  '01_Executive',
  '02_Sales_Pipeline',
  '03_Contracts_&_Compliance',
  '04_Finance',
  '05_Projects',
  '06_Marketing',
  '07_Legal',
  '08_School_MSU',
];

/**
 * Calendar names to provision.
 */
const CALENDAR_NAMES = [
  'Contracts & Bids',
  'Finance & Invoices',
  'Ops & Field',
  'School/MSU',
];

// ---- Entry points ----

/**
 * Run the entire workspace provisioning workflow.
 */
function runAll() {
  setupGmail();
  setupDrive();
  setupCalendars();
  Logger.log('A+ Workspace provisioning complete.');
}

/**
 * Create Gmail labels, filters, and retroactively apply filters to recent mail.
 */
function setupGmail() {
  const labelMap = ensureLabels_(REQUIRED_LABELS);
  const filterSpecs = [];

  filterSpecs.push(...createVipFilters_(labelMap));
  filterSpecs.push(createOrUpdateFilter_({
    name: 'GovCon/RFP',
    criteria: {
      query: 'subject:(proposal OR RFP OR RFQ OR SOW OR bid OR capability)',
    },
    action: {
      addLabelIds: [labelMap.get('GovCon/RFP')],
    },
  }));

  filterSpecs.push(createOrUpdateFilter_({
    name: 'Finance/Invoices',
    criteria: {
      query: 'invoice OR receipt OR paid OR ACH OR statement',
    },
    action: {
      addLabelIds: [labelMap.get('Finance/Invoices')],
    },
  }));

  filterSpecs.push(createOrUpdateFilter_({
    name: 'Vendors',
    criteria: {
      query:
        'from:(@stripe.com OR @paypal.com OR @gumroad.com OR @upwork.com OR @fiverr.com OR @salesforce.com OR @google.com)',
    },
    action: {
      addLabelIds: [labelMap.get('Vendors')],
    },
  }));

  filterSpecs.push(createOrUpdateFilter_({
    name: 'School/MSU',
    criteria: {
      query: 'from:(@missouristate.edu)',
    },
    action: {
      addLabelIds: [labelMap.get('School/MSU')],
    },
  }));

  filterSpecs.push(createOrUpdateFilter_({
    name: 'Newsletters',
    criteria: {
      query: 'unsubscribe -contract -invoice',
    },
    action: {
      addLabelIds: [labelMap.get('Newsletters')],
      removeLabelIds: ['INBOX'],
    },
  }));

  filterSpecs.push(createOrUpdateFilter_({
    name: 'Internal/Agents',
    criteria: {
      query: `from:(@${INTERNAL_DOMAIN})`,
    },
    action: {
      addLabelIds: [labelMap.get('Internal/Agents')],
    },
  }));

  applyFiltersToRecentThreads_(filterSpecs);
}

/**
 * Create the Drive workspace folder hierarchy.
 */
function setupDrive() {
  const root = ensureTopLevelFolder_('A+ Workspace');
  DRIVE_SUBFOLDERS.forEach((folderName) => {
    const areaFolder = ensureChildFolder_(root, folderName);
    ['01_Inbox', '02_Working', '03_Approved', '99_Archive'].forEach((sub) => {
      ensureChildFolder_(areaFolder, sub);
    });
  });
  Logger.log('Drive workspace ready.');
}

/**
 * Create dedicated calendars for the operating areas.
 */
function setupCalendars() {
  CALENDAR_NAMES.forEach((calendarName) => {
    if (CalendarApp.getCalendarsByName(calendarName).length === 0) {
      CalendarApp.createCalendar(calendarName);
      Logger.log(`Created calendar: ${calendarName}`);
    } else {
      Logger.log(`Calendar already exists: ${calendarName}`);
    }
  });
  Logger.log('Calendar provisioning complete.');
}

// ---- Gmail helpers ----

/**
 * Ensure that each label in {@link labelNames} exists and return a map of
 * label name to label ID for reuse when building filters.
 *
 * @param {string[]} labelNames
 * @return {Map<string, string>} mapping of label name to Gmail label ID.
 */
function ensureLabels_(labelNames) {
  const existingLabels = Gmail.Users.Labels.list('me').labels || [];
  const labelMap = new Map();

  labelNames.forEach((labelName) => {
    let label = existingLabels.find((l) => l.name === labelName);
    if (!label) {
      label = Gmail.Users.Labels.create({
        name: labelName,
        labelListVisibility: 'labelShow',
        messageListVisibility: 'show',
      }, 'me');
      Logger.log(`Created label: ${labelName}`);
    } else {
      Logger.log(`Label already exists: ${labelName}`);
    }
    labelMap.set(labelName, label.id);
  });

  return labelMap;
}

/**
 * Build VIP filters that star messages, keep them out of spam, and apply a
 * label.
 *
 * @param {Map<string, string>} labelMap
 * @return {Object[]} Filter specifications for retroactive processing.
 */
function createVipFilters_(labelMap) {
  const vipFilters = [];
  VIP_CONTACTS.forEach(({ label, addresses }) => {
    if (!addresses || addresses.length === 0) {
      return;
    }
    const labelId = labelMap.get(label);
    const addressQuery = addresses.join(' OR ');
    const criteria = { from: addressQuery };
    const action = {
      addLabelIds: cleanArray_([labelId, 'STARRED']),
      neverSpam: true,
    };
    const filterSpec = createOrUpdateFilter_({
      name: `${label} VIP`,
      criteria,
      action,
    });
    if (filterSpec) {
      vipFilters.push(filterSpec);
    }
  });
  return vipFilters;
}

/**
 * Create a Gmail filter if an identical one does not already exist.
 *
 * @param {Object} spec
 * @param {string} spec.name Friendly descriptor for logging.
 * @param {Object} spec.criteria Gmail API filter criteria definition.
 * @param {Object} spec.action Gmail API filter action definition.
 * @return {Object} Spec augmented with a search query for retroactive use.
 */
function createOrUpdateFilter_(spec) {
  const filters = Gmail.Users.Settings.Filters.list('me').filter || [];
  const normalizedCriteria = normalizeCriteria_(spec.criteria);
  const normalizedAction = normalizeAction_(spec.action);
  const exists = filters.some((filter) => {
    return (
      objectsEqual_(normalizeCriteria_(filter.criteria), normalizedCriteria) &&
      objectsEqual_(normalizeAction_(filter.action), normalizedAction)
    );
  });

  if (!exists) {
    Gmail.Users.Settings.Filters.create({
      criteria: spec.criteria,
      action: spec.action,
    }, 'me');
    Logger.log(`Created filter: ${spec.name}`);
  } else {
    Logger.log(`Filter already exists: ${spec.name}`);
  }

  const searchQuery = buildSearchQuery_(spec.criteria);
  if (!searchQuery) {
    return null;
  }

  return {
    name: spec.name,
    searchQuery,
    action: spec.action,
  };
}

/**
 * Translate filter criteria into a Gmail search query string for
 * retroactive application.
 *
 * @param {Object} criteria Gmail filter criteria.
 * @return {string|null}
 */
function buildSearchQuery_(criteria) {
  if (!criteria) {
    return null;
  }
  if (criteria.query) {
    return criteria.query;
  }
  const parts = [];
  if (criteria.from) {
    parts.push(`from:(${criteria.from})`);
  }
  if (criteria.to) {
    parts.push(`to:(${criteria.to})`);
  }
  if (criteria.subject) {
    parts.push(`subject:(${criteria.subject})`);
  }
  if (criteria.hasTheWord) {
    parts.push(criteria.hasTheWord);
  }
  if (criteria.negatedQuery) {
    parts.push(`-${criteria.negatedQuery}`);
  }
  return parts.length > 0 ? parts.join(' ') : null;
}

/**
 * Apply each filter to the most recent conversations to retroactively add
 * labels, star VIPs, and archive newsletters.
 *
 * @param {Object[]} filterSpecs Filter specifications returned from
 *     {@link createOrUpdateFilter_}.
 */
function applyFiltersToRecentThreads_(filterSpecs) {
  filterSpecs
    .filter(Boolean)
    .forEach(({ name, searchQuery, action }) => {
      const threadIds = searchRecentThreadIds_(searchQuery, THREAD_SAMPLING_LIMIT);
      if (threadIds.length === 0) {
        Logger.log(`No threads to update for: ${name}`);
        return;
      }

      threadIds.forEach((threadId) => {
        Gmail.Users.Threads.modify(
          {
            addLabelIds: cleanArray_(action.addLabelIds),
            removeLabelIds: cleanArray_(action.removeLabelIds),
          },
          'me',
          threadId,
        );

        if (action.addLabelIds && action.addLabelIds.indexOf('STARRED') !== -1) {
          // Ensure the thread is starred for consistency.
          Gmail.Users.Threads.modify({ addLabelIds: ['STARRED'] }, 'me', threadId);
        }
      });

      Logger.log(`Applied filter "${name}" to ${threadIds.length} threads.`);
    });
}

/**
 * Search Gmail for recent threads that match the given query.
 *
 * @param {string} query Gmail search query.
 * @param {number} limit Maximum number of threads to return.
 * @return {string[]} Gmail thread IDs ordered by recency.
 */
function searchRecentThreadIds_(query, limit) {
  if (!query) {
    return [];
  }

  const threadIds = [];
  let pageToken;

  while (threadIds.length < limit) {
    const response = Gmail.Users.Threads.list('me', {
      q: query,
      maxResults: Math.min(500, limit - threadIds.length),
      pageToken,
    });
    const threads = response.threads || [];
    threads.forEach((thread) => {
      if (threadIds.length < limit) {
        threadIds.push(thread.id);
      }
    });
    if (!response.nextPageToken || threadIds.length >= limit) {
      break;
    }
    pageToken = response.nextPageToken;
  }

  return threadIds;
}

/**
 * Normalize filter criteria fields for equality comparison.
 *
 * @param {Object} criteria
 * @return {Object}
 */
function normalizeCriteria_(criteria) {
  const normalized = Object.assign({}, criteria || {});
  return normalized;
}

/**
 * Normalize filter action fields for equality comparison.
 *
 * @param {Object} action
 * @return {Object}
 */
function normalizeAction_(action) {
  if (!action) {
    return {};
  }
  const normalized = Object.assign({}, action);
  if (normalized.addLabelIds) {
    normalized.addLabelIds = cleanArray_(normalized.addLabelIds).sort();
  }
  if (normalized.removeLabelIds) {
    normalized.removeLabelIds = cleanArray_(normalized.removeLabelIds).sort();
  }
  return normalized;
}

/**
 * Shallow comparison helper for plain objects.
 *
 * @param {Object} a
 * @param {Object} b
 * @return {boolean}
 */
function objectsEqual_(a, b) {
  const aKeys = Object.keys(a || {}).sort();
  const bKeys = Object.keys(b || {}).sort();
  if (aKeys.length !== bKeys.length) {
    return false;
  }
  for (let i = 0; i < aKeys.length; i += 1) {
    const key = aKeys[i];
    if (Array.isArray(a[key]) && Array.isArray(b[key])) {
      if (a[key].length !== b[key].length) {
        return false;
      }
      for (let j = 0; j < a[key].length; j += 1) {
        if (a[key][j] !== b[key][j]) {
          return false;
        }
      }
    } else if (a[key] !== b[key]) {
      return false;
    }
  }
  return true;
}

/**
 * Remove falsy entries from an array while preserving order.
 *
 * @param {Array<*>} arr
 * @return {Array<*>}
 */
function cleanArray_(arr) {
  if (!Array.isArray(arr)) {
    return [];
  }
  return arr.filter(Boolean);
}

// ---- Drive helpers ----

/**
 * Locate or create the requested top-level Drive folder.
 *
 * @param {string} name
 * @return {GoogleAppsScript.Drive.Folder}
 */
function ensureTopLevelFolder_(name) {
  const matches = DriveApp.getFoldersByName(name);
  if (matches.hasNext()) {
    return matches.next();
  }
  Logger.log(`Creating top-level folder: ${name}`);
  return DriveApp.createFolder(name);
}

/**
 * Locate or create a child folder under the provided parent.
 *
 * @param {GoogleAppsScript.Drive.Folder} parent
 * @param {string} name
 * @return {GoogleAppsScript.Drive.Folder}
 */
function ensureChildFolder_(parent, name) {
  const matches = parent.getFoldersByName(name);
  if (matches.hasNext()) {
    return matches.next();
  }
  Logger.log(`Creating folder: ${parent.getName()} / ${name}`);
  return parent.createFolder(name);
}
