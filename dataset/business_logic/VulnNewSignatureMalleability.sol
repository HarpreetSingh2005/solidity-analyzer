// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Signature malleability allows replaying the same signature.
contract VulnNewSignatureMalleability {
    mapping(bytes => bool) public usedSignatures; // Should hash the signature or message
    function execute(bytes memory sig) external {
        require(!usedSignatures[sig], "Already used");
        usedSignatures[sig] = true;
        // In ecrecover, an attacker can modify v, r, s to create a different valid sig for the same message
    }
}