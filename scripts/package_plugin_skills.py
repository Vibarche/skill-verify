#!/usr/bin/env python3
"""Build self-contained Claude plugin bundles from canonical skill sources."""
import argparse
import json
import re
import shutil
from pathlib import Path

BUNDLES = {
    'reliability-core': ('agent-memory-audit', 'mcp-agent-hallucination-check'),
    'brain-management': ('setup-brain', 'skill-manager'),
    'tooling': ('connect-tool',),
    'agent-reliability-toolkit': ('agent-memory-architect', 'multi-agent-verifier', 'agent-eval-designer', 'self-hosted-stack-guide', 'skill-architect', 'mcp-agent-hallucination-check'),
}
ROOT = Path(__file__).resolve().parents[1]

def expected_files(skill):
    source = ROOT / 'skills' / skill
    if not (source / 'SKILL.md').is_file():
        raise ValueError(f'Missing canonical SKILL.md: {skill}')
    result = {}
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlinks are not packaged: {path}')
        relative = path.relative_to(source)
        if '__pycache__' in relative.parts or path.suffix == '.pyc':
            continue
        if not path.is_file():
            continue
        data = path.read_bytes()
        if relative.as_posix() == 'SKILL.md':
            text = data.decode('utf-8')
            frontmatter = re.match(r'\A---\s*\n(.*?)\n---(?:\n|$)', text, re.S)
            if not frontmatter:
                raise ValueError(f'Missing frontmatter: {skill}')
            for field in ('name', 'description'):
                if not re.search(rf'^{field}:\s*\S', frontmatter.group(1), re.M):
                    raise ValueError(f'Missing {field}: {skill}')
            prefix = '${CLAUDE_PLUGIN_ROOT}/skills/' + skill + '/'
            head, body = text[:frontmatter.end()], text[frontmatter.end():]
            body = re.sub(r'(?<![\w/])(?:scripts|references)/', lambda m: prefix + m.group(0), body)
            text = head + body
            if skill == 'connect-tool':
                text = text.replace('if they do anyway, pipe it directly into the login command and do not repeat, store, or log it.', 'if a secret is pasted into chat, do not use or repeat it; advise revoking it and generating a replacement locally.')
            data = text.encode('utf-8')
        if path.suffix == '.py':
            compile(data, str(path), 'exec')
        result[relative.as_posix()] = data
    return result

def run(check=False):
    marketplace_path = ROOT / '.claude-plugin' / 'marketplace.json'
    marketplace = json.loads(marketplace_path.read_text())
    entries = {p['name']: p for p in marketplace['plugins']}
    prepared = {}
    for plugin, skills in BUNDLES.items():
        if entries[plugin]['source'] != f'./plugins/{plugin}':
            raise ValueError(f'Unexpected marketplace source: {plugin}')
        manifest_path = ROOT / 'plugins' / plugin / '.claude-plugin' / 'plugin.json'
        manifest = json.loads(manifest_path.read_text())
        if manifest['name'] != plugin:
            raise ValueError(f'Unexpected plugin name: {plugin}')
        manifest['skills'] = './skills'
        manifest['version'] = '1.0.1' if plugin == 'agent-reliability-toolkit' else '0.5.1'
        manifest.pop('documentationUrl', None)
        entries[plugin]['version'] = manifest['version']
        files = {f'{skill}/{name}': data for skill in skills for name, data in expected_files(skill).items()}
        prepared[plugin] = (manifest_path, manifest, files)
    errors = []
    for plugin, (manifest_path, manifest, files) in prepared.items():
        destination = ROOT / 'plugins' / plugin / 'skills'
        if check:
            actual = {}
            if destination.exists():
                for path in destination.rglob('*'):
                    if path.is_symlink():
                        errors.append(f'Symlink in bundle: {path}')
                    elif path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                        actual[path.relative_to(destination).as_posix()] = path.read_bytes()
            if actual != files:
                errors.append(f'Missing, extra or stale bundled files: {plugin}')
            if json.loads(manifest_path.read_text()) != manifest:
                errors.append(f'Stale manifest: {plugin}')
        else:
            if destination.exists():
                shutil.rmtree(destination)
            for relative, data in files.items():
                output = destination / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(data)
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
        print(f'{plugin}: {len(BUNDLES[plugin])} skills, {len(files)} packaged files')
    if check:
        if json.loads(marketplace_path.read_text()) != marketplace:
            errors.append('Stale marketplace versions')
        if errors:
            raise SystemExit('\n'.join(errors))
    else:
        marketplace_path.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail on missing, extra or stale package files; never write')
    run(parser.parse_args().check)
