// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: TWAP With a 1-Block (No) Window
 * CATEGORY: Price Oracle — Insufficient TWAP Duration
 *
 * The contract implements a TWAP but the window is only 1 block (~12s).
 * A single large trade in the previous block is enough to move the TWAP
 * to an arbitrary value. Real-world TWAP windows should be >= 30 minutes
 * to resist single-block manipulation on Ethereum mainnet.
 */
contract TwapShortWindow {
    struct Observation {
        uint256 timestamp;
        uint256 priceCumulative; // sum of instantaneous prices × seconds
    }

    Observation[2] public observations; // ring buffer of size 2
    uint8  public  head;
    uint256 public constant TWAP_WINDOW = 12; // BUG: 1 block ≈ 12 seconds

    // Called by AMM on every trade to update cumulative price
    function update(uint256 spotPrice) external {
        uint8 next = (head + 1) % 2;
        observations[next] = Observation({
            timestamp:       block.timestamp,
            priceCumulative: observations[head].priceCumulative
                             + spotPrice * (block.timestamp - observations[head].timestamp)
        });
        head = next;
    }

    function getTwap() public view returns (uint256) {
        Observation memory current = observations[head];
        Observation memory prev    = observations[(head + 1) % 2];

        uint256 timeElapsed = current.timestamp - prev.timestamp;
        require(timeElapsed >= TWAP_WINDOW, "Window not elapsed");
        // BUG: with TWAP_WINDOW=12s, one manipulated block fully determines price
        return (current.priceCumulative - prev.priceCumulative) / timeElapsed;
    }
}
