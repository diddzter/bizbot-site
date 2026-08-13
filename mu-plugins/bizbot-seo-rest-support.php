<?php
/**
 * Registers Yoast SEO's title/description postmeta for REST API read+write
 * access on every content type this repo's automation touches.
 *
 * Why this exists: Yoast SEO doesn't reliably expose _yoast_wpseo_title /
 * _yoast_wpseo_metadesc as writable REST `meta` fields across all versions
 * out of the box. Rather than have migration/push_to_wp.py and
 * automation/seo_audit.py depend on that undocumented behavior, this
 * mu-plugin explicitly registers them with show_in_rest, so "set the SEO
 * title/description via the REST API" is guaranteed to work regardless of
 * which Yoast version is installed.
 *
 * Deployed to wp-content/mu-plugins/ (see .github/workflows/deploy_theme.yml)
 * so it's always active -- mu-plugins can't be deactivated from wp-admin,
 * which is what you want for something automation depends on.
 */

defined( 'ABSPATH' ) || exit;

add_action( 'init', 'bizbot_register_seo_meta_for_rest' );
function bizbot_register_seo_meta_for_rest() {
	foreach ( array( 'post', 'page', 'tool', 'bb_news' ) as $post_type ) {
		register_post_meta(
			$post_type,
			'_yoast_wpseo_title',
			array(
				'show_in_rest' => true,
				'single'       => true,
				'type'         => 'string',
				'auth_callback' => function () use ( $post_type ) {
					return current_user_can( 'edit_posts' );
				},
			)
		);
		register_post_meta(
			$post_type,
			'_yoast_wpseo_metadesc',
			array(
				'show_in_rest' => true,
				'single'       => true,
				'type'         => 'string',
				'auth_callback' => function () use ( $post_type ) {
					return current_user_can( 'edit_posts' );
				},
			)
		);
	}
}
