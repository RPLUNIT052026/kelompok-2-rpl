import 'package:latlong2/latlong.dart';

import 'evacuation_response.dart';

class NavigationSession {
  const NavigationSession({required this.origin, required this.response});

  final LatLng origin;
  final EvacuationResponse response;

  List<RouteSegment> get reportableSegments {
    final unique = <String, RouteSegment>{};
    for (final route in response.routes) {
      for (final segment in route.segments) {
        unique[segment.segmentId] = segment;
      }
    }
    return unique.values.toList(growable: false);
  }
}
