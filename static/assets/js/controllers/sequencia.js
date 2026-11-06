angular.module('deciframeApp').controller('SequenciaController', function($http, $window, ngProgressFactory, $anchorScroll, $location, GENEROS) {
  var acordesC = [
    { 'acorde': 'C',  'cor': '#e6b300' },
    { 'acorde': 'C#', 'cor': '#e6b300' },
    { 'acorde': 'Cm', 'cor': '#efcc59' },
    { 'acorde': 'C#m','cor': '#efcc59' },
    { 'acorde': 'C7', 'cor': '#d6a602' },
    { 'acorde': 'C#7','cor': '#d6a602' }];
  var acordesD = [
    { 'acorde': 'D',  'cor': '#cb6018' },
    { 'acorde': 'D#', 'cor': '#cb6018' },
    { 'acorde': 'Dm', 'cor': '#cf6f3e' },
    { 'acorde': 'D#m','cor': '#cf6f3e' },
    { 'acorde': 'D7', 'cor': '#bc5a1d' },
    { 'acorde': 'D#7','cor': '#bc5a1d' }];
  var acordesE = [
    { 'acorde': 'E',  'cor': '#b72c52' },
    { 'acorde': 'Em', 'cor': '#c5516e' },
    { 'acorde': 'E7', 'cor': '#a92f4d' }];
  var acordesF = [
    { 'acorde': 'F',  'cor': '#ba007c' },
    { 'acorde': 'F#', 'cor': '#ba007c' },
    { 'acorde': 'Fm', 'cor': '#c02a88' },
    { 'acorde': 'F#m','cor': '#c02a88' },
    { 'acorde': 'F7', 'cor': '#ad0076' },
    { 'acorde': 'F#7','cor': '#ad0076' }];
  var acordesG = [
    { 'acorde': 'G',  'cor': '#7b057e' },
    { 'acorde': 'G#', 'cor': '#7b057e' },
    { 'acorde': 'Gm', 'cor': '#882888' },
    { 'acorde': 'G#m','cor': '#882888' },
    { 'acorde': 'G7', 'cor': '#710c77' },
    { 'acorde': 'G#7','cor': '#710c77' }];
  var acordesA = [
    { 'acorde': 'A',  'cor': '#76aadb' },
    { 'acorde': 'A#', 'cor': '#76aadb' },
    { 'acorde': 'Am', 'cor': '#89c0e9' },
    { 'acorde': 'A#m','cor': '#89c0e9' },
    { 'acorde': 'A7', 'cor': '#6c9ecc' },
    { 'acorde': 'A#7','cor': '#6c9ecc' }];
  var acordesB = [
    { 'acorde': 'B',  'cor': '#a3bd31' },
    { 'acorde': 'Bm', 'cor': '#cdd54f' },
    { 'acorde': 'B7', 'cor': '#96b02f' }];

  var vm = this;
  vm.sequenciasFamosas = [];
  vm.acordes = [];
  vm.acordes.push(acordesC);
  vm.acordes.push(acordesD);
  vm.acordes.push(acordesE);
  vm.acordes.push(acordesF);
  vm.acordes.push(acordesG);
  vm.acordes.push(acordesA);
  vm.acordes.push(acordesB);
  vm.minhaSequencia = {};
  vm.novaSequencia = { acordes: [] };
  vm.isSearching = false;
  vm.showSearchResultsCount = false;
  vm.buscaRealizada = false;
  vm.esfigeSpeech =  "";
  vm.musics = [];
  vm.generos = GENEROS;
  vm.meuGenero = "";
  vm.progressbar = ngProgressFactory.createInstance();
  vm.carregandoSequencias = false;
  vm.erroCarregandoSequencias = "";
  vm.mostrarCadastro = false;
  vm.isCadastrando = false;
  vm.mensagemCadastro = "";
  vm.tipoMensagemCadastro = "";

  vm.carregarSequencias = function() {
    vm.carregandoSequencias = true;
    vm.erroCarregandoSequencias = "";
    $http.get('sequencias')
      .success(function(data) {
        vm.carregandoSequencias = false;
        vm.sequenciasFamosas = (data || []).map(function(sequencia) {
          return {
            id: sequencia.id,
            acordes: (sequencia.acordes || '').split(' ').filter(function(acorde) {
              return acorde;
            }).map(function(acorde) {
              return { 'acorde': acorde, 'cor': '#2E1C74' };
            })
          };
        });
      })
      .error(function() {
        vm.carregandoSequencias = false;
        vm.erroCarregandoSequencias = "Não foi possível carregar as sequências.";
      });
  };

  vm.carregarSequencias();

  vm.temAcorde = function(acorde) {
    if (vm.minhaSequencia.acordes) {
      return (vm.minhaSequencia.acordes.indexOf(acorde) > -1);
    } else {
      return false;
    }
  };

  vm.novaSequenciaTemAcorde = function(acorde) {
    for (var i = 0; i < vm.novaSequencia.acordes.length; i++) {
      if (vm.novaSequencia.acordes[i].acorde === acorde.acorde) {
        return true;
      }
    }
    return false;
  };

  var createChordsString = function(chords) {
    return chords.map(function(acorde) {
      return acorde.acorde;
    }).join(',');
  };

  vm.pesquisarPorSequencia = function(sequencia) {
    if (sequencia) {
      vm.minhaSequencia = sequencia;
    }
    if (!vm.minhaSequencia.acordes || !vm.minhaSequencia.acordes.length) {
      return;
    }

    var params = {
      sequencia: createChordsString(vm.minhaSequencia.acordes)
    };
    if (vm.meuGenero !== "" && vm.meuGenero !== null) {
      params.generos = vm.meuGenero;
    }

    vm.mensagemCadastro = "";
    vm.tipoMensagemCadastro = "";
    vm.progressbar.start();
    vm.esfigeSpeech = "Procurando músicas com base na sequência...";
    vm.isSearching = true;
    vm.musics = [];
    vm.showSearchResultsCount = false;
    vm.buscaRealizada = false;

    $http.get('similares', { params: params })
      .success(function(data) {
        vm.progressbar.complete();
        vm.isSearching = false;
        vm.buscaRealizada = true;
        vm.musics = data || [];
        vm.esfigeSpeech = vm.musics.length ? "Encontrei essas músicas" : "Nenhuma música encontrada";
        vm.showSearchResultsCount = vm.musics.length > 0;
      })
      .error(function() {
        vm.progressbar.complete();
        vm.esfigeSpeech = "Ops! Algo errado.";
        vm.isSearching = false;
        vm.buscaRealizada = false;
        vm.showSearchResultsCount = false;
      });
  }

  vm.limparPesquisa = function() {
    vm.minhaSequencia = {};
    vm.musics = [];
    vm.isSearching = false;
    vm.showSearchResultsCount = false;
    vm.buscaRealizada = false;
    vm.esfigeSpeech = "";
  }

  vm.goToLirics = function(music) {
    $window.open(music.url);
  };

  vm.goToResults = function() {
    vm.showSearchResultsCount = false;
    $("body").animate({scrollTop: $("#results").offset().top}, "slow");
  };

  vm.abrirCadastro = function() {
    vm.mostrarCadastro = true;
    vm.mensagemCadastro = "";
    vm.tipoMensagemCadastro = "";
  };

  vm.fecharMensagemCadastro = function() {
    vm.mensagemCadastro = "";
    vm.tipoMensagemCadastro = "";
  };

  vm.fecharCadastro = function() {
    vm.mostrarCadastro = false;
    vm.limparNovaSequencia();
  };

  vm.limparNovaSequencia = function() {
    vm.novaSequencia = { acordes: [] };
    vm.mensagemCadastro = "";
    vm.tipoMensagemCadastro = "";
  };

  vm.addAcordeNovaSequencia = function(acorde) {
    vm.novaSequencia.acordes.push({ 'acorde': acorde.acorde, 'cor': acorde.cor });
    vm.mensagemCadastro = "";
    vm.tipoMensagemCadastro = "";
  };

  vm.removerAcordeNovaSequencia = function(index) {
    vm.novaSequencia.acordes.splice(index, 1);
    vm.mensagemCadastro = "";
    vm.tipoMensagemCadastro = "";
  };

  vm.cadastrarSequencia = function() {
    if (!vm.novaSequencia.acordes.length || vm.isCadastrando) {
      return;
    }

    var acordes = vm.novaSequencia.acordes.map(function(acorde) {
      return acorde.acorde;
    }).join(' ');

    vm.isCadastrando = true;
    vm.mensagemCadastro = "";
    vm.tipoMensagemCadastro = "";

    $http.post('sequencias', { acordes: acordes })
      .success(function() {
        vm.isCadastrando = false;
        vm.mostrarCadastro = false;
        vm.novaSequencia = { acordes: [] };
        vm.mensagemCadastro = "Sequência cadastrada com sucesso.";
        vm.tipoMensagemCadastro = "success";
        vm.carregarSequencias();
      })
      .error(function(data, status) {
        vm.isCadastrando = false;
        vm.tipoMensagemCadastro = "danger";
        if (status === 409) {
          vm.mensagemCadastro = "Essa sequência já existe.";
        } else if (status === 400) {
          vm.mensagemCadastro = (data && data.erro) ? data.erro : "Não foi possível cadastrar a sequência.";
        } else {
          vm.mensagemCadastro = "Erro ao cadastrar a sequência. Tente novamente.";
        }
      });
  };
});
