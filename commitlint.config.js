module.exports = {
    extends: ['@commitlint/config-conventional'],
    rules: {
      'type-enum': [
        2,
        'always',
        [
          'feat',     // nouvelle fonctionnalité
          'fix',      // correction de bug
          'docs',     // documentation
          'style',    // formatage, point-virgules manquants, etc.
          'refactor', // refactoring du code
          'test',     // ajout ou modification de tests
          'chore',    // maintenance (dépendances, build, etc.)
          'perf',     // amélioration des performances
          'ci',       // intégration continue
          'build',    // système de build
          'revert'    // annulation d'un commit précédent
        ]
      ],
      'subject-max-length': [2, 'always', 72],
      'subject-case': [2, 'always', 'lower-case'],
      'header-max-length': [2, 'always', 100]
    }
  };