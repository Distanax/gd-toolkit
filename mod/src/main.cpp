#include <Geode/Geode.hpp>

using namespace geode::prelude;

$on_mod(Loaded) {
	log::info("GD Bridge {} loaded; save dir {}", Mod::get()->getVersion().toVString(),
		utils::string::pathToString(Mod::get()->getSaveDir()));
}
