// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract TwapShortWindow {
    struct Observation { uint256 timestamp; uint256 priceCumulative; }
    Observation[2] public observations;
    uint8 public head;
    uint256 public constant TWAP_WINDOW = 12; // BUG: too short
    function update(uint256 spotPrice) external {
        uint8 next = (head + 1) % 2;
        observations[next] = Observation(block.timestamp, observations[head].priceCumulative + spotPrice * (block.timestamp - observations[head].timestamp));
        head = next;
    }
}