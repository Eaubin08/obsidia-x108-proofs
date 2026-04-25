import fs from 'fs';
import path from 'path';

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
}

export class ExplorerService {
  public static scan(dir: string): FileNode[] {
    const results: FileNode[] = [];
    const list = fs.readdirSync(dir);

    for (const file of list) {
      if (file === 'node_modules' || file === '.git' || file === 'dist') continue;
      
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat && stat.isDirectory()) {
        results.push({
          name: file,
          path: filePath,
          type: 'directory',
          children: this.scan(filePath)
        });
      } else {
        results.push({
          name: file,
          path: filePath,
          type: 'file'
        });
      }
    }
    return results;
  }

  public static getSystemArchitecture(): FileNode[] {
    return [
      {
        name: 'OS0: CENTRE SOUVERAIN',
        path: 'system/os0',
        type: 'directory',
        children: [
          { name: 'Kernel Arbitre', path: 'system/os0/decision', type: 'file' },
          { name: 'Layer A Screening', path: 'system/os0/ingest', type: 'file' },
          { name: 'Grammaire Système', path: 'system/os0/grammar', type: 'file' },
          { name: 'Constitution Inter-couches', path: 'system/os0/constitution', type: 'file' }
        ]
      },
      {
        name: 'OS1: ENTRÉE / RÉEL',
        path: 'system/os1',
        type: 'directory',
        children: [
          { name: 'Canonisation du Réel', path: 'system/os1/canon', type: 'file' },
          { name: 'Needs Engine', path: 'system/os1/needs', type: 'file' },
          { name: 'Reflex Zone', path: 'system/os1/reflex', type: 'file' },
          { name: 'Upstream Connectors', path: 'system/os1/upstream', type: 'file' }
        ]
      },
      {
        name: 'OS2: RECHERCHE / EXPLORATION',
        path: 'system/os2',
        type: 'directory',
        children: [
          { name: 'Knowledge Graph', path: 'system/os2/knowledge', type: 'file' },
          { name: 'Search Engine', path: 'system/os2/search', type: 'file' },
          { name: 'Quantum Research', path: 'system/os2/quantum', type: 'file' }
        ]
      },
      {
        name: 'OS3: MONDE / INTERACTION',
        path: 'system/os3',
        type: 'directory',
        children: [
          { name: 'Interface Logic', path: 'system/os3/ui', type: 'file' },
          { name: 'External Connectors', path: 'system/os3/connectors', type: 'file' },
          { name: 'World State Alignment', path: 'system/os3/alignment', type: 'file' }
        ]
      },
      {
        name: 'SIGMA: TRAJECTORY ENGINE',
        path: 'system/sigma',
        type: 'directory',
        children: [
          { name: 'Trajectory Prediction', path: 'system/sigma/prediction', type: 'file' },
          { name: 'Becoming Engine', path: 'system/sigma/becoming', type: 'file' },
          { name: 'Future State Mapping', path: 'system/sigma/mapping', type: 'file' }
        ]
      },
      {
        name: 'GPS: GLOBAL POSITIONING SYSTEM',
        path: 'system/gps',
        type: 'directory',
        children: [
          { name: 'Spatial Sovereignty', path: 'system/gps/spatial', type: 'file' },
          { name: 'Geofencing Logic', path: 'system/gps/geofence', type: 'file' },
          { name: 'Local Context Mapping', path: 'system/gps/context', type: 'file' }
        ]
      },
      {
        name: 'OS4: PREUVE / AUDIT',
        path: 'system/os4',
        type: 'directory',
        children: [
          { name: 'Traceability', path: 'system/os4/trace', type: 'file' },
          { name: 'Verification', path: 'system/os4/verify', type: 'file' },
          { name: 'Proof of Sovereignty', path: 'system/os4/proof', type: 'file' }
        ]
      },
      {
        name: 'OS5: FONDATIONS / INFRA',
        path: 'system/os5',
        type: 'directory',
        children: [
          { name: 'Storage Engine', path: 'system/os5/storage', type: 'file' },
          { name: 'Identity Provider', path: 'system/os5/idp', type: 'file' },
          { name: 'Hardware Abstraction', path: 'system/os5/hal', type: 'file' }
        ]
      }
    ];
  }
}
