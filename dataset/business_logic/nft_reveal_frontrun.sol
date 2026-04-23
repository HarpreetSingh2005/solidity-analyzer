// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract NFTRevealFrontrun {
    function reveal(uint256 tokenId) external {
        uint256 seed = uint256(blockhash(block.number - 1)) ^ tokenId;
        uint8 rarity = uint8(seed % 100);
        // BUG: blockhash is predictable → front-running possible
    }
}