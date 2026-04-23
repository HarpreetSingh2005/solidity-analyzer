// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: abi.encodePacked hash collision with dynamic types.
contract VulnNewHashCollision {
    mapping(bytes32 => bool) public executed;
    function execute(string memory a, string memory b) external {
        bytes32 hash = keccak256(abi.encodePacked(a, b));
        require(!executed[hash], "Executed");
        executed[hash] = true;
        // "a", "bc" and "ab", "c" produce the same hash
    }
}