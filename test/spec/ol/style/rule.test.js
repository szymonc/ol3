goog.provide('ol.test.style.Rule');

describe('ol.style.Rule', function() {

  describe('#applies()', function() {
    var feature = new ol.Feature(),
        rule;

    it('returns true for a rule without filter', function() {
      rule = new ol.style.Rule({});
      expect(rule.applies(feature)).to.be(true);
    });

    it('returns false when the rule does not apply', function() {
      rule = new ol.style.Rule({
        filter: new ol.filter.Filter(function() { return false; })
      });
      expect(rule.applies(feature)).to.be(false);
    });

    it('returns true when the rule applies', function() {
      rule = new ol.style.Rule({
        filter: new ol.filter.Filter(function() { return true; })
      });
      expect(rule.applies(feature)).to.be(true);
    });
  });

});

goog.require('ol.Feature');
goog.require('ol.filter.Filter');
goog.require('ol.style.Rule');
