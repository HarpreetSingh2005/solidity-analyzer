// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Delegatecall to user-controlled address.
contract VulnNewDelegateCall {
    function execute(address target, bytes memory data) external {
        (bool success, ) = target.delegatecall(data); // Attacker can execute arbitrary code in this contract's context
        require(success);
    }
}