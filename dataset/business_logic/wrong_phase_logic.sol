// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract WrongPhaseLogic {
    enum Phase { Seed, Private, Public }
    Phase public currentPhase = Phase.Seed;
    function buyTokens() external payable {
        require(currentPhase == Phase.Public, "Not public sale"); // BUG: wrong phase check
    }
}