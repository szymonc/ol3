/**
 * @license
 * Latitude/longitude spherical geodesy formulae taken from
 * http://www.movable-type.co.uk/scripts/latlong.html
 * Licenced under CC-BY-3.0.
 */

// FIXME add intersection of two paths given start points and bearings
// FIXME add rhumb lines

goog.provide('ol.Sphere');

goog.require('goog.math');
goog.require('ol.Coordinate');



/**
 * @constructor
 * @param {number} radius Radius.
 */
ol.Sphere = function(radius) {

  /**
   * @type {number}
   */
  this.radius = radius;

};


/**
 * Returns the distance from c1 to c2 using the spherical law of cosines.
 *
 * @param {ol.Coordinate} c1 Coordinate 1.
 * @param {ol.Coordinate} c2 Coordinate 2.
 * @return {number} Spherical law of cosines distance.
 */
ol.Sphere.prototype.cosineDistance = function(c1, c2) {
  var lat1 = goog.math.toRadians(c1.y);
  var lat2 = goog.math.toRadians(c2.y);
  var deltaLon = goog.math.toRadians(c2.x - c1.x);
  return this.radius * Math.acos(
      Math.sin(lat1) * Math.sin(lat2) +
      Math.cos(lat1) * Math.cos(lat2) * Math.cos(deltaLon));
};


/**
 * Returns the distance of c3 from the great circle path defined by c1 and c2.
 *
 * @param {ol.Coordinate} c1 Coordinate 1.
 * @param {ol.Coordinate} c2 Coordinate 2.
 * @param {ol.Coordinate} c3 Coordinate 3.
 * @return {number} Cross-track distance.
 */
ol.Sphere.prototype.crossTrackDistance = function(c1, c2, c3) {
  var d12 = this.cosineDistance(c1, c2);
  var d13 = this.cosineDistance(c1, c2);
  var theta12 = goog.math.toRadians(this.initialBearing(c1, c2));
  var theta13 = goog.math.toRadians(this.initialBearing(c1, c3));
  return this.radius *
      Math.asin(Math.sin(d13 / this.radius) * Math.sin(theta13 - theta12));
};


/**
 * Returns the distance from c1 to c2 using Pythagoras's theorem on an
 * equirectangular projection.
 *
 * @param {ol.Coordinate} c1 Coordinate 1.
 * @param {ol.Coordinate} c2 Coordinate 2.
 * @return {number} Equirectangular distance.
 */
ol.Sphere.prototype.equirectangularDistance = function(c1, c2) {
  var lat1 = goog.math.toRadians(c1.y);
  var lat2 = goog.math.toRadians(c2.y);
  var deltaLon = goog.math.toRadians(c2.x - c1.x);
  var x = deltaLon * Math.cos((lat1 + lat2) / 2);
  var y = lat2 - lat1;
  return this.radius * Math.sqrt(x * x + y * y);
};


/**
 * Returns the final bearing from c1 to c2.
 *
 * @param {ol.Coordinate} c1 Coordinate 1.
 * @param {ol.Coordinate} c2 Coordinate 2.
 * @return {number} Initial bearing.
 */
ol.Sphere.prototype.finalBearing = function(c1, c2) {
  return (this.initialBearing(c2, c1) + 180) % 360;
};


/**
 * Returns the distance from c1 to c2 using the haversine formula.
 *
 * @param {ol.Coordinate} c1 Coordinate 1.
 * @param {ol.Coordinate} c2 Coordinate 2.
 * @return {number} Haversine distance.
 */
ol.Sphere.prototype.haversineDistance = function(c1, c2) {
  var lat1 = goog.math.toRadians(c1.y);
  var lat2 = goog.math.toRadians(c2.y);
  var deltaLatBy2 = (lat2 - lat1) / 2;
  var deltaLonBy2 = goog.math.toRadians(c2.x - c1.x) / 2;
  var a = Math.sin(deltaLatBy2) * Math.sin(deltaLatBy2) +
      Math.sin(deltaLonBy2) * Math.sin(deltaLonBy2) *
      Math.cos(lat1) * Math.cos(lat2);
  return 2 * this.radius * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
};


/**
 * Returns the initial bearing from c1 to c2.
 *
 * @param {ol.Coordinate} c1 Coordinate 1.
 * @param {ol.Coordinate} c2 Coordinate 2.
 * @return {number} Initial bearing.
 */
ol.Sphere.prototype.initialBearing = function(c1, c2) {
  var lat1 = goog.math.toRadians(c1.y);
  var lat2 = goog.math.toRadians(c2.y);
  var deltaLon = goog.math.toRadians(c2.x - c1.x);
  var y = Math.sin(deltaLon) * Math.cos(lat2);
  var x = Math.cos(lat1) * Math.sin(lat2) -
      Math.sin(lat1) * Math.cos(lat2) * Math.cos(deltaLon);
  return goog.math.toDegrees(Math.atan2(y, x));
};


/**
 * Returns the maximum latitude of the great circle defined by bearing and
 * latitude.
 *
 * @param {number} bearing Bearing.
 * @param {number} latitude Latitude.
 * @return {number} Maximum latitude.
 */
ol.Sphere.prototype.maximumLatitude = function(bearing, latitude) {
  return Math.cos(Math.abs(Math.sin(goog.math.toRadians(bearing)) *
                           Math.cos(goog.math.toRadians(latitude))));
};


/**
 * Returns the midpoint between c1 and c2.
 *
 * @param {ol.Coordinate} c1 Coordinate 1.
 * @param {ol.Coordinate} c2 Coordinate 2.
 * @return {ol.Coordinate} Midpoint.
 */
ol.Sphere.prototype.midpoint = function(c1, c2) {
  var lat1 = goog.math.toRadians(c1.y);
  var lat2 = goog.math.toRadians(c2.y);
  var lon1 = goog.math.toRadians(c1.x);
  var deltaLon = goog.math.toRadians(c2.x - c1.x);
  var Bx = Math.cos(lat2) * Math.cos(deltaLon);
  var By = Math.cos(lat2) * Math.sin(deltaLon);
  var cosLat1PlusBx = Math.cos(lat1) + Bx;
  var lat = Math.atan2(Math.sin(lat1) + Math.sin(lat2),
                       Math.sqrt(cosLat1PlusBx * cosLat1PlusBx + By * By));
  var lon = lon1 + Math.atan2(By, cosLat1PlusBx);
  return new ol.Coordinate(goog.math.toDegrees(lon), goog.math.toDegrees(lat));
};


/**
 * Returns the coordinate at the given distance and bearing from c.
 *
 * @param {ol.Coordinate} c1 Coordinate.
 * @param {number} distance Distance.
 * @param {number} bearing Bearing.
 * @return {ol.Coordinate} Coordinate.
 */
ol.Sphere.prototype.offset = function(c1, distance, bearing) {
  var lat1 = goog.math.toRadians(c1.y);
  var lon1 = goog.math.toRadians(c1.x);
  var dByR = distance / this.radius;
  var lat = Math.asin(
      Math.sin(lat1) * Math.cos(dByR) +
      Math.cos(lat1) * Math.sin(dByR) * Math.cos(bearing));
  var lon = lon1 + Math.atan2(
      Math.sin(bearing) * Math.sin(dByR) * Math.cos(lat1),
      Math.cos(dByR) - Math.sin(lat1) * Math.sin(lat));
  return new ol.Coordinate(goog.math.toDegrees(lon), goog.math.toDegrees(lat));
};
