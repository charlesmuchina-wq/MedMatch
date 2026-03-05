/**
 * LUMI Shared Constants
 * ESY Color Theme: Pink (#E84393), Turquoise (#00CEC9), Deep Red (#D63031)
 */

export const API = process.env.REACT_APP_BACKEND_URL;
export const WS_URL = API.replace('https://', 'wss://').replace('http://', 'ws://');

export const ESY = {
  pink: '#E84393',
  pinkLight: '#FD79A8',
  turquoise: '#00CEC9',
  turquoiseLight: '#55EFC4',
  deepRed: '#D63031',
  deepRedLight: '#FF7675',
};

export const STATUS_COLORS = {
  available: 'bg-emerald-500',
  busy: 'bg-amber-500',
  in_meeting: 'bg-red-500',
  ooo: 'bg-red-500',
  vacation: 'bg-red-500',
  offline: 'bg-slate-400',
};

export const STATUS_LABELS = {
  available: 'Available',
  busy: 'Busy',
  in_meeting: 'In a meeting',
  ooo: 'Out of office',
  vacation: 'On vacation',
  offline: 'Offline',
};
